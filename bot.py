from aiogram import Bot, Dispatcher, executor, types
from core.config import BOT_TOKEN, SUPERADMIN_ID
from core.logger import logger
from handlers.grind import register_grind_handlers

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

register_grind_handlers(dp, bot)

if __name__ == "__main__":
    logger.info("🚀 Запуск бота...")
    executor.start_polling(dp, skip_updates=True)
