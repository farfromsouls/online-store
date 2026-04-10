import asyncio
import logging
import json
import os
import sqlite3
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
import redis.asyncio as redis

TOKEN = os.getenv("BOT_TOKEN")
REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = int(os.getenv("REDIS_PORT"))
REDIS_DB = 1
QUEUE_KEY = "bot:notifications"

bot = Bot(token=TOKEN)
dp = Dispatcher()

redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)

db_path = 'data.sqlite3'
conn = sqlite3.connect(db_path, check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS Users (
    id INTEGER PRIMARY KEY,
    last_message TEXT
)
''')
conn.commit()

async def is_admin(uid: int) -> bool:
    cursor.execute("SELECT id FROM Users WHERE id=?", (uid,))
    return cursor.fetchone() is not None

async def add_admin(uid: int):
    cursor.execute("INSERT OR IGNORE INTO Users (id) VALUES (?)", (uid,))
    conn.commit()

async def get_all_admins():
    cursor.execute("SELECT id FROM Users")
    return [row[0] for row in cursor.fetchall()]

async def auth(user_input):
    data = {
        "login": user_input[0],
        "password": user_input[1]
    }
    response = requests.post('http://web:8000/account/auth/', data=data)
    return response

async def send_notification_to_admins(notification):
    admins = await get_all_admins()
    if not admins:
        logging.warning("Нет админов для отправки уведомления")
        return

    user = notification.get('user', 'Неизвестный')
    items = notification.get('items', {})
    timestamp = notification.get('timestamp', '')

    text = f"🛒 <b>Новая покупка!</b>\n👤 Пользователь: {user}\n📦 Товары:\n"
    for product_id, qty in items.items():
        text += f"  • Товар #{product_id}: {qty} шт.\n"
    if timestamp:
        text += f"⏱ Время: {timestamp}\n"

    for admin_id in admins:
        try:
            await bot.send_message(admin_id, text, parse_mode="HTML")
        except Exception as e:
            logging.error(f"Не удалось отправить админу {admin_id}: {e}")

async def redis_listener():
    while True:
        try:
            result = await redis_client.brpop(QUEUE_KEY, timeout=1)
            if result:
                _, data = result
                notification = json.loads(data)
                await send_notification_to_admins(notification)
            await asyncio.sleep(0.1)
        except Exception as e:
            logging.error(f"Ошибка в Redis listener: {e}")
            await asyncio.sleep(5)

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Введите логин и пароль (через пробел)")

@dp.message()
async def handler(message: types.Message):
    uid = message.from_user.id
    text = message.text

    if await is_admin(uid):
        await message.answer("Вы уже админ")
        return

    parts = text.split()
    if len(parts) != 2:
        await message.answer("Введите логин и пароль (через пробел)")
        return

    response = await auth(parts)
    if response.json().get("success"):
        await add_admin(uid)
        await message.answer("✅ Вы успешно авторизованы как администратор!")
    else:
        await message.answer("❌ Неверные данные")

async def main():
    asyncio.create_task(redis_listener())
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())