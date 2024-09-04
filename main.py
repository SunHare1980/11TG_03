from aiogram.fsm.context import FSMContext

from config import TOKEN, APIKEY, JAKEY
import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, FSInputFile
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
import requests
import sqlite3

bot = Bot(token=TOKEN)
dp = Dispatcher()

class Form(StatesGroup):
    name = State()
    age = State()
    grade = State()

@dp.message(Command('help'))
async def help(message: Message, state: FSMContext):
    await message.answer("Этот бот умеет выполнять команды:\n/start\n/help\n/Weather")
    await state.set_state(Form.name)

@dp.message(Form.name)
async def name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Сколько тебе лет?")
    await state.set_state(Form.age)

@dp.message(Form.age)
async def age(message: Message, state: FSMContext):
    await state.update_data(age=message.text)
    await message.answer("Из какой ты группы?")
    await state.set_state(Form.grade)

@dp.message(Form.grade)
async def grade(message: Message, state:FSMContext):
    await state.update_data(grade=message.text)
    user_data = await state.get_data()
    conn = sqlite3.connect('bot.db')
    cur = conn.cursor()
    cur.execute('''
    INSERT INTO students (name, age, grade) VALUES (?, ?, ?)''', (user_data['name'], user_data['age'], user_data['grade']))
    conn.commit()
    conn.close()
    await message.answer("Данные добавлены в БД")
    await state.clear()
@dp.message(Command('Weather'))
async def help(message: Message):
    weather = get_weather('Kursk')
    await message.answer("Погода в городе Курск "+ str(weather['main']['temp'])+"°C\n"+str(weather['weather'][0]['description']))

@dp.message(CommandStart())
async def start(message: Message, state: FSMContext):
    await message.answer("Привет! Как тебя зовут?")
    await state.set_state(Form.name)

async def main():
    await dp.start_polling(bot)

def get_weather(city):
   api_key = APIKEY
   #адрес, по которомы мы будем отправлять запрос. Не забываем указывать f строку.
   url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&lang=ru&units=metric"
   #для получения результата нам понадобится модуль requests
   response = requests.get(url)
   #прописываем формат возврата результата
   return response.json()
@dp.message(F.photo)
async def react_photo(message: Message):
    await bot.download(message.photo[-1],destination=f'img/{message.photo[-1].file_id}.jpg')


def translate_text(text, api_key):
    url = "https://translate.api.cloud.yandex.net/translate/v2/translate"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Api-Key {api_key}"
    }

    body = {
        "targetLanguageCode": "en",
        "texts": [text],
        "folderId": "b1ggie2lfmuj3ilan7uj"  # замените на ваш идентификатор каталога
    }

    response = requests.post(url, headers=headers, json=body)

    if response.status_code == 200:
        translated_texts = response.json().get("translations", [])
        if translated_texts:
            return translated_texts[0].get("text", "")
    else:
        print(f"Error: {response.status_code} - {response.text}")

    return None


if __name__ == "__main__":
    conn = sqlite3.connect('bot.db')
    cur = conn.cursor()
    cur.execute('''
    CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    age INTEGER,
    grade TEXT);''')

    conn.commit()
    conn.close()
    asyncio.run(main())


    # { % if weather %}
    # < h3 > Погода
    # в
    # {{weather['name']}} < / h3 >
    # < p > Температура: {{weather['main']['temp']}}°C < / p >
    # < p > Погода: {{weather['weather'][0]['description']}} < / p >
