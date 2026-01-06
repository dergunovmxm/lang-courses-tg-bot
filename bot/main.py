import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import asyncio
from aiogram import Bot, Dispatcher
from config import Config
from database.connection import postgresql_client
from app.handlers.start import get_start_handler
from app.handlers.info import get_info_handler
from app.handlers.timer import get_timer_handler
from app.handlers.profile import get_profile_handler
from utils.startup_utils import show_startup_message
import logging
from app.handlers.testing import get_test_handler
from app.handlers.audio import get_audio_handler
from app.handlers.task_flow import get_task_handler
logger = logging.getLogger(__name__)

# Создание бота и диспетчера
bot = Bot(token=Config.BOT_TOKEN)
dp = Dispatcher()

async def on_startup(bot: Bot):

    #Функция, выполняемая при запуске бота
    try:
        # Валидация конфигурации
        Config.validate()
        # Тестирование подключения к PostgreSQL
        if postgresql_client.test_connection():
            logger.info("✅ Подключение к PostgreSQL успешно установлено")
            print("✅ Подключение к PostgreSQL успешно установлено")

        else:
            logger.error("❌ Не удалось подключиться к PostgreSQL")
            print("❌ Не удалось подключиться к PostgreSQL")
            return False
        
        # Регистрация роутеров
        dp.include_router(get_start_handler())
        dp.include_router(get_info_handler())
        dp.include_router(get_timer_handler())
        dp.include_router(get_profile_handler())
        dp.include_router(get_test_handler())
        dp.include_router(get_audio_handler())
        dp.include_router(get_task_handler())
        print('include succesfully')
        # Отправка сообщения о запуске (опционально)
        await show_startup_message(bot)
        return True
        
    except Exception as e:
        logger.error(f"❌ Ошибка при запуске бота: {e}")
        print(f"❌ Ошибка при запуске бота: {e}")
        return False

async def on_shutdown():
    #Функция, выполняемая при остановке бота
    try:
        # Закрытие соединения с базой данных
        if hasattr(postgresql_client, 'close'):
            postgresql_client.close()
            logger.info("✅ Соединение с PostgreSQL закрыто")
            print("✅ Соединение с PostgreSQL закрыто")
        logger.info("🔸 Бот остановлен")
        print("🔸 Бот остановлен")

    except Exception as e:
        logger.error(f"❌ Ошибка при остановке бота: {e}")
        print(f"❌ Ошибка при остановке бота: {e}")

async def main():

    #Основная функция запуска бота
    
    try:
        await on_startup(bot)
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")
        print(f"❌ Критическая ошибка: {e}")
    finally:
        await on_shutdown()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🔸 Бот остановлен по команде пользователя (Ctrl+C)")

    except Exception as e:
        logger.error(f"❌ Неожиданная ошибка: {e}")
        print(f"❌ Неожиданная ошибка: {e}")