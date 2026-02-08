import asyncio
import aiohttp
import markovify
import re
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from bs4 import BeautifulSoup

# --- НАСТРОЙКИ ---
TOKEN = "8090178058:AAGwwYNUvE0xEhf4GKVtKOmw8wahSl_x8QM"
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Файл, где хранится интеллект Luum
BRAIN_STORAGE = "luum_knowledge.txt"

# --- ЛОГИКА ОБУЧЕНИЯ И МЫШЛЕНИЯ ---
def train_and_generate(text_input):
    # Сохраняем новые знания
    with open(BRAIN_STORAGE, "a", encoding="utf-8") as f:
        f.write(text_input + ". ")
    
    # Читаем накопленный опыт
    with open(BRAIN_STORAGE, "r", encoding="utf-8") as f:
        knowledge_base = f.read()
    
    # Если база слишком маленькая (меньше 3-4 предложений), ИИ не сможет составить фразу
    if len(knowledge_base.split()) < 10:
        return "Я собираю данные... Мне нужно больше твоих мыслей, чтобы заговорить."

    try:
        # Создаем модель на основе накопленных данных
        # state_size=2 делает речь более связной
        model = markovify.Text(knowledge_base, state_size=2)
        
        # Генерируем уникальное предложение
        response = model.make_sentence(tries=100)
        
        return response if response else "Мои нейроны связываются... Продолжай общение."
    except:
        return "Произошла перестройка нейронной сети. Повтори запрос."

# --- ПАРСЕР ДЛЯ ОБУЧЕНИЯ НА САЙТАХ ---
async def learn_from_site(url):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as resp:
                soup = BeautifulSoup(await resp.text(), 'html.parser')
                # Выкачиваем чистый текст из статей
                for tag in soup(["script", "style", "nav", "footer"]): tag.decompose()
                clean_text = " ".join(soup.get_text().split())
                return clean_text[:2000] # Берем приличный кусок для обучения
    except:
        return None

# --- ОБРАБОТЧИКИ ---

@dp.message(Command("start"))
async def cmd_start(m: types.Message):
    await m.answer(
        "🧠 **Luum: Система локального ИИ запущена.**\n\n"
        "Я работаю без внешних генераторов. Мой разум строится только на твоих словах.\n\n"
        "• Пиши мне что угодно — я учусь.\n"
        "• Присылай ссылки — я заберу знания оттуда."
    )

@dp.message(F.text.regexp(r'(https?://\S+)'))
async def handle_link(m: types.Message):
    url = re.findall(r'(https?://\S+)', m.text)[0]
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🧠 Поглотить знания сайта", callback_data=f"learn|{url}")]
    ])
    await m.answer("🌐 Вижу источник информации. Позволишь мне изучить его?", reply_markup=kb)

@dp.callback_query(F.data.startswith("learn|"))
async def process_learning(c: types.CallbackQuery):
    url = c.data.split("|")[1]
    await c.answer("Изучаю контент...")
    
    site_data = await learn_from_site(url)
    if site_data:
        # Luum обучается на тексте сайта
        reply = train_and_generate(site_data)
        await c.message.answer(f"✅ Знания получены. Вот мой вывод на основе новой инфо:\n\n{reply}")
    else:
        await c.message.answer("❌ Не удалось дотянуться до данных.")

@dp.message()
async def chat_handler(m: types.Message):
    if not m.text: return
    
    # Обучаемся на сообщении пользователя и генерируем ответ
    response = train_and_generate(m.text)
    await m.answer(response)

# --- ЗАПУСК ---
async def main():
    # Создаем базу знаний, если её нет
    open(BRAIN_STORAGE, "a").close()
    print("🤖 Luum готова к обучению. Админка и фото отключены.")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
