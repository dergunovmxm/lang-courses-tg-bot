from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

router = Router()

@router.message(CommandStart())
async def handle_start(message: Message):
    await message.answer("Привет! Это твой бот. " \
    "Для показа информации нажмите /info")