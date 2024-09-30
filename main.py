import asyncio
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
import aiohttp
import sqlite3
import logging

from config import TOKEN, weather_api

bot = Bot(token=TOKEN) # https://t.me/aio_bot_my_bot
dp = Dispatcher()

logging.basicConfig(level=logging.INFO) #создание логгера INFO - выводит информацию о событиях,
# ERROR - ошибка в работе бота, DEBUG - отладка программы

class Form(StatesGroup):
    name = State()
    age = State()
    grade = State()

def init_db():
    conn = sqlite3.connect('school_data.db') # подключение к БД, если такой базы нет, то она будет создана,
    # а если она есть, то она будет использоваться
    cur= conn.cursor() # создание курсора, через него будем выполнять запросы к БД
    cur.execute("""CREATE TABLE IF NOT EXISTS students( 
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        age INTEGER NOT NULL,
        grade TEXT NOT NULL)""")
    conn.commit() # сохраняем изменения
    conn.close() # закрываем соединение c БД

init_db()

@dp.message(CommandStart()) # если получим команду /start
# то будет запускаться функция для которой прописан этот декоратор
async def start(message: Message, state: FSMContext):
    await message.answer("Привет, студент. Как тебя зовут?")
    await state.set_state(Form.name) # ожидание ввода имени

@dp.message(Form.name) # если получим имя
# то будет запускаться функция для которой прописан этот декоратор
async def name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Сколько тебе лет?")
    await state.set_state(Form.age) # ожидание ввода возраста

@dp.message(Form.age) # если получим возраст
# то будет запускаться функция для которой прописан этот декоратор
async def age(message: Message, state: FSMContext):
    await state.update_data(age=message.text)
    await message.answer("Какая у тебя оценка?")
    await state.set_state(Form.grade) # ожидание ввода оценки

@dp.message(Form.grade) # если получим оценку
# то будет запускаться функция для которой прописан этот декоратор
async def grade(message: Message, state: FSMContext):
    await state.update_data(grade=message.text)
    student_data = await state.get_data() # получение данных из состояния бота

    conn = sqlite3.connect('school_data.db') # подключение к БД, если такой базы нет, то она будет создана,
    # а если она есть, то она будет использоваться
    cur = conn.cursor() # создание курсора, через него будем выполнять запросы к БД
    cur.execute("""INSERT INTO students(name, age, grade) VALUES(?,?,?)""", (student_data['name'], student_data['age'], student_data['grade']))
    conn.commit() # сохраняем изменения
    conn.close() # закрываем соединение c БД

    await message.answer("Данные сохранены")
    await state.clear()

#чтение базы данных
@dp.message(Command('read_db'))
async def read_db(message: Message):
    conn = sqlite3.connect('school_data.db') # подключение к БД, если такой базы нет, то она будет создана,
    # а если она есть, то она будет использоваться
    cur = conn.cursor() # создание курсора, через него будем выполнять запросы к БД
    cur.execute("""SELECT * FROM students""")
    data = cur.fetchall() # получение данных
    conn.close() # закрываем соединение c БД
    if data:
        for row in data:
            await message.answer(f"ID: {row[0]}\nИмя: {row[1]}\nВозраст: {row[2]}\nОценка: {row[3]}")
    else:
        await message.answer("База данных пуста")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())