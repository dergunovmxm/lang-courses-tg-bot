from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
import logging
import asyncio
from datetime import datetime

logger = logging.getLogger(__name__)

router = Router()

# Словарь для хранения активных таймеров
active_timers = {}

@router.message(Command("timer"))
async def handle_timer(message: Message):

    #Обработчик команды /timer - запускает/останавливает таймер

    user = message.from_user
    
    # Проверяем, есть ли уже активный таймер для пользователя
    if user.id in active_timers:
        # Останавливаем таймер
        await stop_timer(user.id, message)
    else:
        # Запускаем таймер
        await start_timer(user.id, message)

async def start_timer(user_id: int, message: Message):
    
    #Запускает таймер для пользователя

    try:
        # Отправляем сообщение о запуске таймера
        start_message = await message.answer(
            "⏰ Таймер запущен!\n"
            "Я буду отправлять уведомления каждые 10 секунд.\n"
            "Для остановки снова нажмите /timer"
        )
        
        # Сохраняем ID сообщения для возможного редактирования
        active_timers[user_id] = {
            'task': None,
            'start_time': datetime.now(),
            'message_id': start_message.message_id,
            'counter': 0
        }
        
        # Запускаем асинхронную задачу
        task = asyncio.create_task(timer_loop(user_id, message.bot, message.chat.id))
        active_timers[user_id]['task'] = task
        
        
    except Exception as e:
        logger.error(f"Ошибка при запуске таймера для пользователя {user_id}: {e}")
        await message.answer("❌ Не удалось запустить таймер")

async def stop_timer(user_id: int, message: Message):

    #Останавливает таймер 

    try:
        timer_data = active_timers.get(user_id)
        if timer_data and timer_data['task']:
            # Отменяем задачу
            timer_data['task'].cancel()
            
            # Удаляем из активных таймеров
            del active_timers[user_id]
            
            # Создаем запись о учебной сессии
            stop_message = (
                "🛑 Таймер остановлен!"
            )
            
            await message.answer(stop_message)
            logger.info(f"Таймер остановлен для пользователя {user_id}")
            
    except Exception as e:
        logger.error(f"Ошибка при остановке таймера для пользователя {user_id}: {e}")
        await message.answer("❌ Не удалось остановить таймер")

async def timer_loop(user_id: int, bot, chat_id: int):

    #Цикл таймера, отправляющий сообщения каждые 10 секунд

    try:
        counter = 0
        while True:
            # Ждем 10 секунд
            await asyncio.sleep(10)
            counter += 1
            
            # Обновляем счетчик в активных таймерах
            if user_id in active_timers:
                active_timers[user_id]['counter'] = counter
            
            # Отправляем уведомление
            notification_text = (
                f"🔔 Уведомление #{counter}\n"
                f"⏱ Прошло: {counter * 10} секунд\n"
                "🛑 Для остановки нажмите /timer"
            )
            
            await bot.send_message(chat_id, notification_text)
            logger.debug(f"Отправлено уведомление #{counter} пользователю {user_id}")
            
    except asyncio.CancelledError:
        # Задача была отменена 
        logger.debug(f"Таймерная задача отменена для пользователя {user_id}")
    except Exception as e:
        logger.error(f"Ошибка в таймерe для пользователя {user_id}: {e}")
        # Удаляем таймер при ошибке
        if user_id in active_timers:
            del active_timers[user_id]

@router.message(Command("timer_status"))
async def handle_timer_status(message: Message):

    #Показывает статус активных таймеров (для отладки)

    user = message.from_user
    
    if user.id in active_timers:
        timer_data = active_timers[user.id]
        status_text = (
            "📊 Статус таймера:\n"
            f"• Запущен: {timer_data['start_time'].strftime('%H:%M:%S')}\n"
            f"• Отправлено уведомлений: {timer_data['counter']}\n"
            f"• Прошло времени: {timer_data['counter'] * 10} секунд\n"
            "🛑 Для остановки нажмите /timer"
        )
    else:
        status_text = "⏰ Таймер не активен\nДля запуска нажмите /timer"
    
    await message.answer(status_text)

def get_timer_handler():
    return router