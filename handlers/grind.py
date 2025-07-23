import asyncio
import time
from aiogram import types, Dispatcher, Bot
from pathlib import Path
from utils.process_manager import ProcessManager
from core.logger import logger
from core.config import SUPERADMIN_ID
import re

process_manager = ProcessManager()

def register_grind_handlers(dp: Dispatcher, bot: Bot):
    @dp.message_handler(commands=["grind"])
    async def grind_command(message: types.Message):
        if message.from_user.id not in SUPERADMIN_ID:
            logger.warning(f"⛔ Пользователь {message.from_user.id} попытался использовать /grind без прав")
            return await message.reply("⛔ Доступ запрещён")

        if process_manager.is_running(message.from_user.id):
            logger.info(f"⏳ Пользователь {message.from_user.id} уже выполняет задачу")
            return await message.reply("⌛ Уже выполняется задача. Напиши /cancel для отмены.")

        args = message.get_args()
        if not args:
            return await message.reply("⚠️ Укажи префикс: /grind serg", parse_mode="HTML")

        prefix = args.strip()

        cmd = [
            "solana-keygen", "grind",
            "--starts-with", f"{prefix}:1",
            "--num-threads", "4"
        ]

        start_time = time.time()
        logger.info(f"🚀 Запущен grind для '{prefix}' пользователем {message.from_user.id}")

        progress_message = await message.reply(
            f"⏳ Ищу адрес с префиксом <code>{prefix}</code>. Напиши /cancel чтобы прервать.",
            parse_mode="HTML"
        )

        async def progress_updater():
            while process_manager.is_running(message.from_user.id):
                elapsed = int(time.time() - start_time)
                await asyncio.sleep(10)
                try:
                    await progress_message.edit_text(
                        f"⏳ Всё ещё ищу адрес с префиксом <code>{prefix}</code>\nПрошло: <b>{elapsed}</b> секунд",
                        parse_mode="HTML"
                    )
                except Exception as e:
                    logger.warning(f"⚠️ Не удалось обновить сообщение прогресса: {e}")

        updater_task = asyncio.create_task(progress_updater())

        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd="/tmp"
        )
        process_manager.add(message.from_user.id, proc)

        try:
            stdout, stderr = await proc.communicate()
        except asyncio.CancelledError:
            proc.kill()
            await proc.wait()
            process_manager.remove(message.from_user.id)
            updater_task.cancel()
            logger.info(f"❌ Процесс отменён пользователем {message.from_user.id}")
            return await message.reply("❌ Поиск отменён.")

        stdout_text = stdout.decode()
        stderr_text = stderr.decode()

        process_manager.remove(message.from_user.id)
        updater_task.cancel()

        if proc.returncode != 0:
            logger.error(f"❌ Ошибка процесса для '{prefix}': {stderr_text}")
            return await message.reply(f"❌ Ошибка:\n<pre>{stderr_text}</pre>", parse_mode="HTML")

        # 🕵️ Найдём путь к созданному ключу
        match = re.search(r'Wrote keypair to (.+\.json)', stdout_text)
        if not match:
            logger.error("❌ Не удалось найти путь к сгенерированному ключу в stdout")
            logger.debug(f"stdout:\n{stdout_text}")
            return await message.reply("❌ Не удалось найти файл с ключом.")

        real_keyfile_path = Path("/tmp")/Path(match.group(1)).resolve()

        # 📦 Отправляем файл
        try:
            await message.reply_document(real_keyfile_path.open("rb"), caption=f"📦 Готово! Адрес с '{prefix}'")
            logger.info(f"✅ Ключ отправлен пользователю {message.from_user.id}: {real_keyfile_path.name}")
        except Exception as e:
            logger.error(f"❌ Ошибка при отправке ключа: {e}")
            return await message.reply("❌ Не удалось отправить файл.")

        # 🧹 Удаляем файл
        try:
            real_keyfile_path.unlink()
            logger.info(f"🧹 Удалён временный файл {real_keyfile_path}")
        except Exception as e:
            logger.warning(f"⚠️ Не удалось удалить временный файл: {e}")

    @dp.message_handler(commands=["cancel"])
    async def cancel_command(message: types.Message):
        if message.from_user.id not in SUPERADMIN_ID:
            logger.warning(f"⛔ Пользователь {message.from_user.id} попытался использовать /cancel без прав")
            return await message.reply("⛔ Доступ запрещён")

        result = await process_manager.cancel(message.from_user.id)
        if result:
            logger.info(f"❌ Поиск остановлен пользователем {message.from_user.id}")
            await message.reply("❌ Поиск остановлен.")
        else:
            await message.reply("ℹ️ Нет активного поиска.")
