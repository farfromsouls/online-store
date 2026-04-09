import sqlite3
import requests

db_path = 'data.sqlite3'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS Users (
id INTEGER PRIMARY KEY,
last_message TEXT
)''')

async def is_admin(id):
    cursor.execute(f"SELECT * FROM Users WHERE id={id}")
    response = cursor.fetchall()
    
    if len(response) != 0:
        return True
    return False

async def auth(user_input):
    data = {
        "login": user_input[0],
        "password": user_input[1]
    }
    response = requests.post('http://web:8000/account/auth/', data)
    return response

async def add_admin(id):
    cursor.execute(f"INSERT INTO Users (id) VALUES ({id})")
    conn.commit()