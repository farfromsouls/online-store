from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

import asyncio
import logging
import os


TOKEN = os.getenv("BOT_TOKEN")


test_btn = KeyboardButton(text="test")

main_btn = ReplyKeyboardMarkup(keyboard=[
    [test_btn]
], resize_keyboard=True)

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Тест")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())