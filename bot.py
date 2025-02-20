from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage

import sqlite3
from datetime import datetime
import os

from lunaryapi import ClientLunaryAI, RequestError
from dotenv import load_dotenv

load_dotenv()

bot = Bot(os.getenv("TOKEN_BOT"))
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

connection = sqlite3.connect("data_users.db")
cursor = connection.cursor()

#openai/gpt-4o-mini, openai/gpt-3.5-turbo, deepseek/deepseek-chat, qwen/qvq-72b-preview, 
# eva-unit-01/eva-qwen-2.5-72b, qwen/qwen-2.5-72b-instruct, google/gemini-flash-1.5
# google/gemma-2-9b-it, meta-llama/llama-3.3-70b-instruct, microsoft/phi-4
lunaryBot = ClientLunaryAI(os.getenv("API_KEY"), "google/gemma-2-9b-it")

def output(message: str, warn: bool = False):
    if warn == False:
        print(f"\033[92m[{datetime.now().strftime('%d.%m.%Y %H:%M:%S')}]\033[0m {message}")
    else:
        print(f"\033[93m[{datetime.now().strftime('%d.%m.%Y %H:%M:%S')}] {message}\033[0m")

async def responce_to_user(message: types.Message):
    messagetimer = await bot.send_message(message.chat.id, "Пожалуйста подождите, генерирую ответ...")
    try:
        result = lunaryBot.request_to_api(message.text)
        output(f"{message.from_user.full_name} ({message.from_user.id}, @{message.from_user.username or '-'}) спросил: {message.text}")
        await message.reply(result, parse_mode = "Markdown")
    except RequestError as exp:
        output(f"{message.from_user.full_name} ({message.from_user.id}, @{message.from_user.username or '-'}) получил ошибку: {str(exp)}, ошибка API: {exp.status_code}", warn=True)
        await message.reply(f"Извините, но я не смогу вам ответить. \nЭто не ответ ИИ, а заготовленное сообщение в случае проблемы с настоящим ИИ. Тех.поддержка скоро починит меня и я снова смогу отвечать на ваши промпты.")
    except Exception as exp:
        output(f"{message.from_user.full_name} ({message.from_user.id}, @{message.from_user.username or '-'}) получил ошибку: {str(exp)}", warn=True)
        await message.reply(result)
    await messagetimer.delete()

async def on_startup(_):
    cursor.execute("""CREATE TABLE IF NOT EXISTS users (
        full_name TEXT,
        username TEXT,
        id BIGINT
    )""")
    connection.commit()
    output("Бот готов")

@dp.message_handler(commands=["start"])
async def cmnd(message: types.Message):
    if cursor.execute(f"SELECT username FROM users WHERE id = {message.from_user.id}").fetchone() is None:
        cursor.execute(f"INSERT INTO users VALUES ('{message.from_user.full_name}', '@{message.from_user.username or '-'}', {message.from_user.id})")
        connection.commit()

    await message.reply("🤖 Привет, хочешь пообщаться с настоящим искуственным интелектом Lunary AI? \n💜 Просто напиши свой промпт (или проще говоря вопрос) и я отвечу на него как только смогу")

@dp.message_handler()
async def cmnd(message: types.Message):
    if message.chat.type == "private":
        await responce_to_user(message)
    elif message.chat.type.find("group"):
        if message.text.lower().startswith("lunaryai,"):
            message.text = message.text.removeprefix("lunaryai,")
            await responce_to_user(message)

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)