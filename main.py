from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
import asyncio
import logging
import sys

from config import TOKEN
from app.handlers.start import router as start_router
from app.handlers.info import router as info_router
from app.handlers.timer import router as timer_router
from utils.time_utils import set_bot_start_time
from utils.cmd_logger_utils import on_shutdown, on_startup, register_handlers, active_timers

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('bot.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

# Устанавливаем время старта бота
set_bot_start_time()

BOT_TOKEN = TOKEN
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# Регистрируем роутеры из handlers
dp.include_router(start_router)
dp.include_router(info_router)
dp.include_router(timer_router)

# Регистрируем команды из cmd_logger_utils
register_handlers(dp)

async def main():
    """Основная функция запуска бота"""
    try:
        await on_startup(bot)
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        print(f"❌ Критическая ошибка: {e}")
    finally:
        await on_shutdown(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🔸 Бот остановлен по команде пользователя (Ctrl+C)")
    except Exception as e:
        logger.error(f"Неожиданная ошибка: {e}")
        print(f"❌ Неожиданная ошибка: {e}")