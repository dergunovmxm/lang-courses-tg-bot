import logging
from aiogram import Bot

from .time_utils import get_current_time, get_bot_uptime

logger = logging.getLogger(__name__)

async def show_startup_message(bot: Bot):

    #Показывает сообщение о запуске бота в консоли

    try:
        me = await bot.get_me()
        print("\n" + "="*60)
        print("🤖 БОТ УСПЕШНО ЗАПУЩЕН!")
        print("="*60)
        print(f"📝 Имя бота: {me.full_name}")
        print(f"🔗 Username: @{me.username}")
        print(f"🆔 ID бота: {me.id}")
        print(f"⏰ Время запуска: {get_current_time()}")
        print(f"✅ Статус: АКТИВЕН И ГОТОВ К РАБОТЕ")
        print("="*60)
        print("📋 Доступные команды:")
        print("   /start - Запустить бота")
        print("   /info - Информация о пользователе")
        print("   /timer - Запустить таймер")
        print("   /status - Статус бота")
        print("="*60)
        print("🚀 Бот готов принимать сообщения...")
        print("="*60 + "\n")
        
        logger.info(f"Бот @{me.username} успешно запущен и готов к работе")
    except Exception as e:
        logger.error(f"Ошибка при получении информации о боте: {e}")
        print("❌ Ошибка при запуске бота")

async def show_shutdown_message():

    #Показывает сообщение об остановке бота
    
    print("\n" + "="*60)
    print("🛑 БОТ ОСТАНАВЛИВАЕТСЯ...")
    print("="*60)
    print(f"⏰ Время остановки: {get_current_time()}")
    print(f"⏱️ Общее время работы: {get_bot_uptime()}")
    print("="*60)
    logger.info("Бот остановлен")