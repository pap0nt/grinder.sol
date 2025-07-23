import asyncio
import time
from aiogram import types, Dispatcher, Bot
from pathlib import Path
from utils.process_manager import ProcessManager

process_manager = ProcessManager()

def register_grind_handlers(dp: Dispatcher, bot: Bot):
    @dp.message_handler(commands=["grind"])
    async def grind_command(message: types.Message):
        from config import SUPERADMIN_ID
        if message.from_user.id not in SUPERADMIN_ID:
            return await message.reply("\u26d4\ufe0f Доступ запрещён")

        if process_manager.is_running(message.from_user.id):
            return await message.reply("\u231b Уже выполняется задача. Напиши /cancel для отмены.")

        args = message.get_args()
        if not args:
            return await message.reply("\u26a0\ufe0f Укажи префикс: /grind serg", parse_mode="HTML")

        prefix = args.strip()
        keyfile = Path("/tmp") / f"keypair-{prefix}.json"

        cmd = [
            "solana-keygen", "grind",
            "--starts-with", f"{prefix}:1",
            "--num-threads", "5",
            "--ignore-case",
            "--outfile", str(keyfile)
        ]

        start_time = time.time()
        progress_message = await message.reply(
            f"\u23f3 Ищу адрес с префиксом <code>{prefix}</code>. Напиши /cancel чтобы прервать.",
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
                except Exception:
                    pass

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
            return await message.reply("\u274c Поиск отменён.")

        process_manager.remove(message.from_user.id)
        updater_task.cancel()

        if proc.returncode != 0:
            return await message.reply(f"\u274c Ошибка:\n<pre>{stderr.decode()}</pre>", parse_mode="HTML")

        if keyfile.exists():
            await message.reply_document(keyfile.open("rb"), caption=f"\ud83d\udce6 Готово! Адрес с '{prefix}'")
            keyfile.unlink()
        else:
            await message.reply("\u274c Адрес не найден или файл не создан.")

    @dp.message_handler(commands=["cancel"])
    async def cancel_command(message: types.Message):
        from config import SUPERADMIN_ID
        if message.from_user.id not in SUPERADMIN_ID:
            return await message.reply("\u26d4\ufe0f Доступ запрещён")

        result = await process_manager.cancel(message.from_user.id)
        if result:
            await message.reply("\u274c Поиск остановлен.")
        else:
            await message.reply("\u2139\ufe0f Нет активного поиска.")