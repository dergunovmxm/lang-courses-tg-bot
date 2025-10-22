import logging
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand, Message
from aiogram.filters import Command

from .time_utils import get_current_time, get_bot_uptime
from .startup_utils import show_shutdown_message, show_startup_message

logger = logging.getLogger(__name__)

# Глобальные переменные
active_timers = {}

async def cmd_status(message: Message):
    """Показывает статус бота"""
    status_info = f"""
🤖 *Статус бота:*

✅ *Активен и готов к работе!*
🕐 *Запущен:* {get_current_time()}
⏱️ *В работе:* {get_bot_uptime()}
👥 *Активных таймеров:* {len(active_timers)}

*Доступные команды:*
/start - Запустить бота
/info - Информация о пользователе  
/timer - Запустить таймер
/status - Статус бота

🚀 *Бот работает стабильно!*
"""
    await message.answer(status_info, parse_mode="Markdown")
    logger.info(f"Пользователь {message.from_user.id} запросил статус бота")

async def set_bot_commands(bot: Bot):
    """Устанавливает команды бота"""
    commands = [
        BotCommand(command="/start", description="Запустить бота"),
        BotCommand(command="/info", description="Информация о тебе"),
        BotCommand(command="/timer", description="Запустить таймер"),
        BotCommand(command="/status", description="Статус бота")
    ]
    await bot.set_my_commands(commands)
    logger.info("Команды бота установлены")

async def on_startup(bot: Bot):
    """Действия при запуске бота"""
    logger.info("Запуск бота...")
    await set_bot_commands(bot)
    await show_startup_message(bot)

async def on_shutdown(bot: Bot):
    """Действия при остановке бота"""
    await show_shutdown_message()
    
    # Останавливаем все активные таймеры
    for user_id, timer in active_timers.items():
        if not timer.done():
            timer.cancel()
            logger.info(f"Остановлен таймер для пользователя {user_id}")
    
    await bot.session.close()

def register_handlers(dp: Dispatcher):
    """Регистрирует обработчики команд в диспетчере"""
    dp.message.register(cmd_status, Command("status"))
    logger.info("Команда /status зарегистрирована")