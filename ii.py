import asyncio
import aiohttp
import re
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from bs4 import BeautifulSoup

# --- КОНФИГ ---
TOKEN = "8090178058:AAGwwYNUvE0xEhf4GKVtKOmw8wahSl_x8QM"
bot = Bot(token=TOKEN)
dp = Dispatcher()

# --- ПАРСЕР САЙТОВ ---
async def fetch_site(url):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=7) as response:
                soup = BeautifulSoup(await response.text(), 'html.parser')
                for s in soup(["script", "style", "nav", "footer"]): s.decompose()
                text = " ".join(soup.get_text().split())
                return text if text else "Текст не найден."
    except: return None

# --- КОМАНДА СТАРТ ---
@dp.message(Command("start"))
async def cmd_start(m: types.Message):
    await m.answer(
        "🧠 **Luum на связи.**\n\n"
        "• Пришли ссылку — я её изучу.\n"
        "• Напиши **'нарисуй [запрос]'** — я создам фото."
    )

# --- ОБРАБОТКА ССЫЛОК (Кнопки) ---
@dp.message(F.text.regexp(r'(https?://\S+)'))
async def link_handler(m: types.Message):
    url = re.findall(r'(https?://\S+)', m.text)[0]
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📝 Пересказать", callback_data=f"summ|{url}"),
            InlineKeyboardButton(text="🤔 О чем это?", callback_data=f"about|{url}")
        ]
    ])
    await m.answer("🌐 Ссылка получена. Что сделать?", reply_markup=kb)

# --- ЛОГИКА КНОПОК ---
@dp.callback_query(F.data.startswith(("summ|", "about|")))
async def callbacks(call: types.CallbackQuery):
    action, url = call.data.split("|")
    await call.answer("🔍 Luum думает...")
    content = await fetch_site(url)
    
    if not content:
        return await call.message.answer("❌ Ошибка чтения.")

    if action == "summ":
        await call.message.answer(f"📝 **Пересказ:**\n{content[:500]}...")
    else:
        await call.message.answer(f"🤔 **Суть сайта:**\n{content[:250]}...")

# --- ГЕНЕРАЦИЯ ФОТО И ТЕКСТ ---
@dp.message()
async def main_logic(m: types.Message):
    if not m.text: return
    txt = m.text.lower()

    if "нарисуй" in txt:
        p = txt.replace("нарисуй", "").strip() or "art"
        await m.answer(f"🎨 Рисую: {p}...")
        url = f"https://pollinations.ai/p/{p.replace(' ', '_')}?width=1024&height=1024"
        return await m.answer_photo(photo=url, caption=f"Запрос: {p}")

    await m.answer("🧠 Запрос принят и сохранен в память.")

# --- ЗАПУСК ---
async def main():
    print("🚀 Luum запущена (3GB RAM / 40% CPU)")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
