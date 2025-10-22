from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router()

@router.message(Command('info'))
async def show_info(message: Message):
    user = message.from_user
    await message.answer(f'''Информация о тебе:
ID: {user.id}
Username: {user.username or "Не указан"}      
Full name: {user.first_name or ""} {user.last_name or ""}
''')