from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command

from buttons import *
from data import is_admin, auth, add_admin

import asyncio
import logging
import json
import os


TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Введите логин и пароль (через пробел)")
    
@dp.message()
async def handler(message: types.Message):
    id = message.from_user.id
    text = message.text
    
    if await is_admin(id):
        await message.answer("ты уже админ в аккаунте")
    
    else:
        user_input = text.split()
        
        if len(user_input) != 2:
            await message.answer("Введите логин и пароль (через пробел)")
            return None
        else:
            response = await auth(user_input)
            if response.json().get("success") == True:
                await add_admin(id)
                await message.answer("пушка ты залогинился")
            else:
                await message.answer("направильные данные")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())