from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
import datetime

router = Router()

@router.message(Command('info'))
async def get_info_handler(message: Message):

    #Обработчик команды /info - показывает информацию о пользователе и боте
    user = message.from_user
    
    # Текущая дата
    current_date = datetime.datetime.now().strftime("%d.%m.%Y %H:%M")
    
    # Основное сообщение
    info_text = f"""
📋 <b>ИНФОРМАЦИЯ</b>
⏰ <i>Запрос от {current_date}</i>

👤 <b>Данные пользователя:</b>
├ ID: <code>{user.id}</code>
├ Username: @{user.username or 'не указан'}
├ Имя: {user.first_name or 'Не указано'}
├ Фамилия: {user.last_name or 'Не указана'}
└ Язык: {user.language_code or 'не определен'}

🤖 <b>О боте:</b>
├ Название: GradeUp
├ Назначение: Отслеживание изучения языков
└ Версия: 1.0

🎯 <b>Как использовать:</b>
1. /start - регистрация и начало работы
2. /timer - запустить таймер занятия
3. /profile - посмотреть свою статистику
4. /info - эта справка

💡 <b>Совет:</b> Регулярно занимайтесь для лучшего прогресса!
    """.strip()

    await message.answer(info_text, parse_mode='HTML')

def get_info_handler():
    return router