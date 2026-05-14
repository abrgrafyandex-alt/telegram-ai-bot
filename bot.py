import os
import asyncio
import sys
if sys.platform.startswith('win'):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from openai import AsyncOpenAI

load_dotenv()
bot = Bot(token=os.getenv('TG_TOKEN'))
dp = Dispatcher()
client = AsyncOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv('OPENROUTER_API_KEY'),
)

history = {}

@dp.message(Command('start'))
async def start(message: types.Message):
    user_id = message.from_user.id
    history[user_id] = []
    await message.reply("Привет! Я ИИ-бот. Пиши сообщения, я отвечу и запомню контекст.")

@dp.message()
async def handle_message(message: types.Message):
    user_id = message.from_user.id
    if user_id not in history:
        history[user_id] = []
    history[user_id].append({"role": "user", "content": message.text})
    if len(history[user_id]) > 20:
        history[user_id] = history[user_id][-20:]
    messages = [{"role": "system", "content": "Ты полезный ассистент на русском."}] + history[user_id]
    await message.reply("🤔 Думаю...")
    try:
        response = await client.chat.completions.create(
            model="deepseek/deepseek-chat:free",
            messages=messages
        )
        answer = response.choices[0].message.content
        history[user_id].append({"role": "assistant", "content": answer})
        await message.reply(answer)
    except Exception as e:
        await message.reply("❌ Ошибка: " + str(e))

async def main():
    print("Бот запущен!")
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())