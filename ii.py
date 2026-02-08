import asyncio
import aiohttp
import re
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command

# Для парсинга сайтов
from bs4 import BeautifulSoup

TOKEN = "8090178058:AAGwwYNUvE0xEhf4GKVtKOmw8wahSl_x8QM"
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Оперативная память чата (очистится при перезагрузке бота)
chat_context = {}

async def get_site_data(url):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=5) as resp:
                soup = BeautifulSoup(await resp.text(), 'html.parser')
                for s in soup(["script", "style"]): s.decompose()
                return " ".join(soup.get_text().split())
    except: return None

@dp.message(Command("start"))
async def start(m: types.Message):
    await m.answer(
        "🧠 **Luum ИИ активна**\n\n"
        "• Пиши: **нарисуй [запрос]** для фото\n"
        "• Кидай **ссылку** для анализа\n"
        "• Я помню контекст нашей беседы!"
    )

@dp.message(F.text.regexp(r'(https?://\S+)'))
async def link(m: types.Message):
    url = re.findall(r'(https?://\S+)', m.text)[0]
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📝 Пересказать", callback_data=f"sm|{url}"),
            InlineKeyboardButton(text="🤔 О чем сайт?", callback_data=f"ab|{url}")
        ]
    ])
    await m.answer("🌐 Ссылка поймана. Что сделать?", reply_markup=kb)

@dp.callback_query(F.data.startswith(("sm|", "ab|")))
async def call_link(c: types.CallbackQuery):
    act, url = c.data.split("|")
    await c.answer("Читаю...")
    text = await get_site_data(url)
    if not text: return await c.message.answer("❌ Ошибка доступа.")
    
    res = f"📝 **Пересказ:**\n{text[:500]}..." if act == "sm" else f"🤔 **Суть:**\n{text[:250]}..."
    await c.message.answer(res)

@dp.message()
async def talk(m: types.Message):
    if not m.text: return
    uid = m.from_user.id
    txt = m.text.lower()

    if uid not in chat_context: chat_context[uid] = []

    # Генерация фото
    if "нарисуй" in txt:
        p = txt.replace("нарисуй", "").strip() or "space"
        await m.answer("🎨 Генерирую...")
        return await m.answer_photo(photo=f"https://pollinations.ai/p/{p.replace(' ', '_')}")

    # Запоминание контекста
    chat_context[uid].append(m.text)
    if len(chat_context[uid]) > 15: chat_context[uid].pop(0)

    # Команда на проверку памяти
    if "вспомни" in txt or "что я писал" in txt:
        history = "\n- ".join(chat_context[uid][-5:])
        return await m.answer(f"🧠 Твои последние мысли:\n- {history}")

    await m.answer("🧠 Поняла. Добавила в текущий контекст.")

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
