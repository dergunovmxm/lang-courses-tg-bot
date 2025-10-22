from aiogram import Router, types
from aiogram.filters import Text

router = Router()

@router.message()
async def echo_handler(message: types.Message):
    await message.answer("Вы сказали: " + message.text)