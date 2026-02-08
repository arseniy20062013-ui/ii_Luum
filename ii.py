import asyncio
import sqlite3
import aiohttp
import re
import torch
import torch.nn as nn
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from bs4 import BeautifulSoup

# --- КОНФИГ ---
TOKEN_LUUM = "8090178058:AAGwwYNUvE0xEhf4GKVtKOmw8wahSl_x8QM"
bot = Bot(token=TOKEN_LUUM)
dp = Dispatcher()

# --- БД (Память нейросети) ---
conn = sqlite3.connect('luum_memory.db', check_same_thread=False)
cur = conn.cursor()
cur.execute('CREATE TABLE IF NOT EXISTS history (user_id INTEGER, role TEXT, content TEXT)')
conn.commit()

# --- КЛАВИАТУРА ---
main_kb = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="🎨 Нарисуй город будущего")],
    [KeyboardButton(text="🌐 Проанализируй ссылку")]
], resize_keyboard=True)

# --- МОДУЛЬ ИНТЕРНЕТА (ПЕРЕСКАЗ) ---
async def summarize_site(url):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=7) as resp:
                soup = BeautifulSoup(await resp.text(), 'html.parser')
                for s in soup(["script", "style", "nav", "footer"]): s.decompose()
                clean_text = " ".join(soup.get_text().split())
                return f"📋 **Анализ Luum:**\n\n{clean_text[:500]}..."
    except:
        return "❌ Не удалось прочитать сайт."

# --- ЛОГИКА LUUM ---

@dp.message(Command("start"), F.bot.token == TOKEN_LUUM)
async def luum_start(m: types.Message):
    await m.answer(
        "🧠 **Luum активирована.**\n\nЯ — твоя автономная нейросеть. "
        "Я использую ресурсы сервера для анализа данных.\n\n"
        "Пришли ссылку для пересказа или попроси 'нарисуй ...'", 
        reply_markup=main_kb
    )

@dp.message(F.bot.token == TOKEN_LUUM)
async def luum_logic(m: types.Message):
    if not m.text: return
    txt = m.text.lower()

    # 1. Анализ ссылок
    urls = re.findall(r'(https?://\S+)', txt)
    if urls:
        await m.answer("📡 Вхожу в сеть... Сканирую протоколы сайта...")
        res = await summarize_site(urls[0])
        return await m.answer(res)

    # 2. Генерация изображений (через API Pollinations - не грузит твою ОЗУ)
    if any(x in txt for x in ["нарисуй", "фото", "картинка"]):
        prompt = txt.replace("нарисуй", "").replace("фото", "").strip() or "nebula"
        await m.answer(f"🎨 Визуализация запроса: {prompt}...")
        img_url = f"https://pollinations.ai/p/{prompt.replace(' ', '_')}?width=1024&height=1024"
        return await m.answer_photo(photo=img_url, caption=f"Готово. Это моё видение '{prompt}'")

    # 3. Сохранение в память и ответ
    cur.execute('INSERT INTO history VALUES (?, ?, ?)', (m.from_user.id, "user", m.text))
    conn.commit()
    
    # Имитируем работу процессора
    await m.answer("🧠 Данные получены. Я встроила это в свою базу знаний для дальнейшего обучения.")

# --- ЗАПУСК ПО ТВОЕМУ ОБРАЗЦУ ---
async def main():
    print("🤖 Luum запущен в режиме AI-сервера.")
    await dp.start_polling(bot, skip_updates=True)

if __name__ == "__main__":
    asyncio.run(main())
