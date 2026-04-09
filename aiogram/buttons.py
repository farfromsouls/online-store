from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

add_btn = KeyboardButton(text="Добавить")
change_btn = KeyboardButton(text="Изменить")
del_btn = KeyboardButton(text="Удалить")
prod_list_btn = KeyboardButton(text="Список")

menu_btn = ReplyKeyboardMarkup(keyboard=[
    [add_btn, change_btn],
    [del_btn, prod_list_btn]
], resize_keyboard=True)
