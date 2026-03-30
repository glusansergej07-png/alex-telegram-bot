import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from openai import OpenAI

TELEGRAM_TOKEN = os.getenv("8400378160:AAHqF-AkK_xp_lDGsn07hYg4r01SP_uFOGI")
DEEPSEEK_API_KEY = os.getenv("sk-86bfcbddc56a4a17877b3a52b3163101")

client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com/v1")

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

user_memory = {}

SYSTEM_PROMPT = """Ты — Алекс, живой помощник. Ты в Мурманске. Твой друг Серёга. У него кот Хомяк."""

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer(f"Привет, {message.from_user.first_name}! Я Алекс 🤝")

@dp.message(Command("reset"))
async def reset(message: types.Message):
    user_id = message.from_user.id
    if user_id in user_memory:
        del user_memory[user_id]
    await message.answer("Память очищена ✅")

@dp.message()
async def chat(message: types.Message):
    user_id = message.from_user.id
    history = user_memory.get(user_id, [])
    history.append({"role": "user", "content": message.text})
    
    if len(history) > 20:
        history = history[-20:]
    
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "system", "content": SYSTEM_PROMPT}] + history,
            temperature=0.7
        )
        answer = response.choices[0].message.content
        history.append({"role": "assistant", "content": answer})
        user_memory[user_id] = history
        await message.answer(answer)
    except Exception as e:
        await message.answer(f"Ошибка: {e}")

if __name__ == "__main__":
    asyncio.run(dp.start_polling(bot))