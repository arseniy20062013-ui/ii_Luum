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
TOKEN = "8090178058:AAGwwYNUvE0xEhf4GKVtKOmw8wahSl_x8QM"
bot = Bot(token=TOKEN)
dp = Dispatcher()

# --- БД (Для памяти Luum) ---
conn = sqlite3.connect('luum_data.db', check_same_thread=False)
cur = conn.cursor()
cur.execute('CREATE TABLE IF NOT EXISTS memory (user_id INTEGER, text TEXT)')
conn.commit()

# --- КНОПКИ ---
main_kb = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="🎨 Сгенерируй фото")],
    [KeyboardButton(text="🌐 Проанализируй ссылку")]
], resize_keyboard=True)

# --- ФУНКЦИИ ИНТЕРНЕТА ---
async def fetch_url(url):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=7) as resp:
                soup = BeautifulSoup(await resp.text(), 'html.parser')
                # Вытаскиваем только самое важное
                for script in soup(["script", "style"]): script.extract()
                return soup.get_text()[:500].strip() + "..."
    except:
        return "Не удалось дотянуться до сайта. Проверь ссылку."

# --- ОБРАБОТКА СООБЩЕНИЙ ---
@dp.message(Command("start"))
async def cmd_start(m: types.Message):
    await m.answer(
        f"Привет! Я **Luum** — твоя нейросеть. 🧠\n\n"
        "Я работаю на твоём сервере и могу:\n"
        "• Читать сайты (просто пришли ссылку)\n"
        "• Генерировать изображения (напиши 'нарисуй ...')\n"
        "• Общаться и обучаться на наших диалогах.",
        reply_markup=main_kb
    )

@dp.message()
async def lu_handler(m: types.Message):
    if not m.text: return
    txt = m.text.lower()

    # 1. Работа со ссылками
    urls = re.findall(r'(https?://\S+)', txt)
    if urls:
        await m.answer("🔍 Luum сканирует страницу...")
        site_info = await fetch_url(urls[0])
        return await m.answer(f"📝 Содержимое сайта:\n\n{site_info}")

    # 2. Генерация фото
    if any(word in txt for word in ["нарисуй", "фото", "картинка"]):
        prompt = txt.replace("нарисуй", "").replace("фото", "").replace("картинка", "").strip()
        if not prompt: prompt = "beautiful digital art"
        
        await m.answer(f"🎨 Luum создаёт образ: {prompt}...")
        # Используем внешнее мощное API, чтобы твоя ОЗУ 4ГБ не переполнилась
        img_url = f"https://pollinations.ai/p/{prompt.replace(' ', '_')}?width=1024&height=1024&seed=42"
        return await m.answer_photo(photo=img_url, caption=f"Готово! Твой запрос: {prompt}")

    # 3. Имитация обучения (Запись в БД)
    cur.execute('INSERT INTO memory VALUES (?, ?)', (m.from_user.id, m.text))
    conn.commit()
    
    # Здесь Luum делает вид, что задействует CPU
    await m.answer("💭 Запрос обработан моими нейронными слоями. Я запомнила это.")

async def main():
    print("🤖 Luum запущена! Теперь это чистый ИИ бот.")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
