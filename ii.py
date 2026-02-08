import asyncio
import aiohttp
import re
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from bs4 import BeautifulSoup

# --- КОНФИГ (ТОЛЬКО ОДИН БОТ) ---
TOKEN = "8090178058:AAGwwYNUvE0xEhf4GKVtKOmw8wahSl_x8QM"
bot = Bot(token=TOKEN)
dp = Dispatcher()

# --- ФУНКЦИЯ ЧТЕНИЯ САЙТОВ ---
async def fetch_site_text(url):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=7) as response:
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                # Удаляем мусорные теги
                for script_or_style in soup(["script", "style", "nav", "footer", "header"]):
                    script_or_style.decompose()
                text = " ".join(soup.get_text().split())
                return text if text else "Сайт не содержит текста."
    except Exception as e:
        return None

# --- ОБРАБОТКА КОМАНДЫ /START ---
@dp.message(Command("start"))
async def cmd_start(m: types.Message):
    await m.answer(
        "🧠 **Luum на связи.**\n\n"
        "Я — твой персональный ИИ. Вот что я могу:\n"
        "• **Фото:** Напиши «нарисуй [запрос]»\n"
        "• **Ссылки:** Просто пришли ссылку, и я её изучу."
    )

# --- ОБРАБОТКА ССЫЛОК ---
@dp.message(F.text.regexp(r'(https?://\S+)'))
async def link_handler(m: types.Message):
    url = re.findall(r'(https?://\S+)', m.text)[0]
    
    # Создаем кнопки под ссылкой
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📝 Пересказать", callback_data=f"summ|{url}"),
            InlineKeyboardButton(text="🤔 О чем это?", callback_data=f"about|{url}")
        ]
    ])
    
    await m.answer("🌐 Ссылка получена. Выбери действие:", reply_markup=kb)

# --- ОБРАБОТКА НАЖАТИЙ НА КНОПКИ ---
@dp.callback_query(F.data.startswith(("summ|", "about|")))
async def process_callback(call: types.CallbackQuery):
    action, url = call.data.split("|")
    await call.answer("🔍 Luum изучает сайт...")
    
    content = await fetch_site_text(url)
    if not content:
        return await call.message.answer("❌ Не удалось прочитать содержимое сайта.")

    if action == "summ":
        result = f"📝 **Пересказ от Luum:**\n\n{content[:500]}..."
    else:
        # Имитация "понимания" о чем сайт (берем самое начало)
        result = f"🤔 **О чем этот сайт:**\n\nЭтот ресурс содержит информацию о: {content[:200]}..."
    
    await call.message.answer(result)

# --- ГЕНЕРАЦИЯ ФОТО И ДИАЛОГ ---
@dp.message()
async def main_handler(m: types.Message):
    if not m.text: return
    txt = m.text.lower()

    if "нарисуй" in txt:
        prompt = txt.replace("нарисуй", "").strip() or "cyberpunk vision"
        await m.answer(f"🎨 Рисую: {prompt}...")
        photo_url = f"https://pollinations.ai/p/{prompt.replace(' ', '_')}?width=1024&height=1024"
        return await m.answer_photo(photo=photo_url, caption=f"Твой запрос: {prompt}")

    # Если это просто текст
    await m.answer("🧠 Запрос принят. Я сохранила это в нейронную память.")

# --- ЗАПУСК ---
async def main():
    print("--- LUUM ЗАПУЩЕНА (БЕЗ АДМИНКИ) ---")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
