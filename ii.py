import asyncio
import sqlite3
import aiohttp
import re
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from bs4 import BeautifulSoup

# --- ТОКЕН ---
TOKEN = "8090178058:AAGwwYNUvE0xEhf4GKVtKOmw8wahSl_x8QM"
bot = Bot(token=TOKEN)
dp = Dispatcher()

# --- БД (SQLite идеально для Termux) ---
conn = sqlite3.connect('luum.db', check_same_thread=False)
cur = conn.cursor()
cur.execute('CREATE TABLE IF NOT EXISTS logs (txt TEXT)')
conn.commit()

# --- ПАРСЕР САЙТОВ ---
async def read_site(url):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as r:
                s = BeautifulSoup(await r.text(), 'html.parser')
                return " ".join(s.get_text().split())[:500] + "..."
    except: return "🚫 Ошибка чтения."

# --- ЛОГИКА ---
@dp.message(Command("start"))
async def s(m: types.Message):
    print(f">>> Бот увидел /start от {m.from_user.username}")
    await m.answer("🧠 Luum в Termux запущена!\nПришли ссылку или 'нарисуй (что-то)'")

@dp.message()
async def h(m: types.Message):
    if not m.text: return
    print(f">>> Сообщение: {m.text}") # Это ты увидишь в терминале
    
    t = m.text.lower()

    if "http" in t:
        url = re.findall(r'(https?://\S+)', t)[0]
        await m.answer("🔍 Читаю сайт...")
        await m.answer(await read_site(url))
    
    elif "нарисуй" in t:
        p = t.replace("нарисуй", "").strip()
        await m.answer(f"🎨 Рисую {p}...")
        url = f"https://pollinations.ai/p/{p.replace(' ', '_')}"
        await m.answer_photo(photo=url)
    
    else:
        cur.execute('INSERT INTO logs VALUES (?)', (m.text,))
        conn.commit()
        await m.answer("🧠 Записала в память сервера.")

async def main():
    print("--- LUUM СТАРТУЕТ В TERMUX ---")
    print("Нажми 'Acquire wakelock' в шторке уведомлений!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
