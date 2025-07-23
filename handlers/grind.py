import asyncio
import time
from aiogram import types, Dispatcher, Bot
from pathlib import Path
from utils.process_manager import ProcessManager
from core.logger import logger
from core.config import SUPERADMIN_ID

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
        keyfile = Path("/tmp") / f"keypair-{prefix}.json"

        cmd = [
            "solana-keygen", "grind",
            "--starts-with", f"{prefix}:1",
            "--num-threads", "5",
            "--ignore-case",
            "--no-outfile"
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
            stderr=asyncio.subprocess.PIPE
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

        process_manager.remove(message.from_user.id)
        updater_task.cancel()

        if proc.returncode != 0:
            logger.error(f"❌ Ошибка процесса для '{prefix}': {stderr.decode()}")
            return await message.reply(f"❌ Ошибка:\n<pre>{stderr.decode()}</pre>", parse_mode="HTML")

        # 💾 Сохраняем stdout в файл
        try:
            with open(keyfile, "wb") as f:
                f.write(stdout)
            logger.info(f"💾 Ключи сохранены в файл {keyfile}")
        except Exception as e:
            logger.error(f"❌ Не удалось сохранить ключи: {e}")
            return await message.reply("❌ Не удалось сохранить ключи.")

        await message.reply_document(keyfile.open("rb"), caption=f"📦 Готово! Адрес с '{prefix}'")
        logger.info(f"✅ Успешно найден адрес для '{prefix}' пользователем {message.from_user.id}")

        try:
            keyfile.unlink()
            logger.info(f"🧹 Файл {keyfile} удалён после отправки")
        except Exception as e:
            logger.warning(f"⚠️ Не удалось удалить временный файл {keyfile}: {e}")


    @dp.message_handler(commands=["cancel"])
    async def cancel_command(message: types.Message):
        from config import SUPERADMIN_ID
        if message.from_user.id not in SUPERADMIN_ID:
            logger.warning(f"⛔ Пользователь {message.from_user.id} попытался использовать /cancel без прав")
            return await message.reply("\u26d4\ufe0f Доступ запрещён")

        result = await process_manager.cancel(message.from_user.id)
        if result:
            logger.info(f"❌ Поиск остановлен пользователем {message.from_user.id}")
            await message.reply("\u274c Поиск остановлен.")
        else:
            await message.reply("\u2139\ufe0f Нет активного поиска.")
