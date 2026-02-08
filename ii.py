import asyncio
import aiohttp
import markovify
import re
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from bs4 import BeautifulSoup

# КОНФИГ
TOKEN = "8090178058:AAGwwYNUvE0xEhf4GKVtKOmw8wahSl_x8QM"
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Файл базы знаний
BRAIN_STORAGE = "luum_knowledge.txt"

# ЛОГИКА МЫШЛЕНИЯ
def train_and_generate(text_input):
    # Очистка текста и запись в базу
    clean_input = text_input.replace("\n", " ").strip()
    if len(clean_input) > 2:
        with open(BRAIN_STORAGE, "a", encoding="utf-8") as f:
            f.write(clean_input + ". ")
    
    with open(BRAIN_STORAGE, "r", encoding="utf-8") as f:
        knowledge = f.read()
    
    if len(knowledge.split()) < 15:
        return "Я только активировалась и пока изучаю твой стиль общения. Напиши мне еще что-нибудь."

    try:
        # Модель с state_size=2 для более качественной речи
        model = markovify.Text(knowledge, state_size=2)
        response = model.make_sentence(tries=100)
        
        # Если не удалось собрать длинное предложение, пробуем короткое
        if not response:
            model = markovify.Text(knowledge, state_size=1)
            response = model.make_sentence(tries=50)
            
        return response if response else "Интересная мысль. Расскажи об этом подробнее?"
    except:
        return "Мои нейронные связи перестраиваются. Давай продолжим диалог."

# ПАРСЕР САЙТОВ ДЛЯ ОБУЧЕНИЯ
async def learn_from_site(url):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as resp:
                soup = BeautifulSoup(await resp.text(), 'html.parser')
                for tag in soup(["script", "style", "nav", "footer", "header"]):
                    tag.decompose()
                clean_text = " ".join(soup.get_text().split())
                return clean_text[:3000]
    except:
        return None

# ОБРАБОТЧИКИ

@dp.message(Command("start"))
async def cmd_start(m: types.Message):
    await m.answer(
        "Привет! Я Luum — твоя персональная нейросеть.\n\n"
        "Я работаю автономно на этом сервере. У меня нет заготовленных фраз: "
        "я учусь прямо сейчас на твоих сообщениях. Чем больше мы общаемся, "
        "тем лучше я буду тебя понимать.\n\n"
        "Просто напиши мне что-нибудь или пришли ссылку на интересную статью."
    )

@dp.message(F.text.regexp(r'(https?://\S+)'))
async def handle_link(m: types.Message):
    url = re.findall(r'(https?://\S+)', m.text)[0]
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Изучить содержимое", callback_data=f"learn|{url}")]
    ])
    await m.answer("Вижу ссылку. Позволишь мне прочитать этот ресурс и обучиться?", reply_markup=kb)

@dp.callback_query(F.data.startswith("learn|"))
async def process_learning(c: types.CallbackQuery):
    url = c.data.split("|")[1]
    await c.answer("Сканирую текст...")
    
    site_data = await learn_from_site(url)
    if site_data:
        # Luum забирает текст сайта в свою базу
        reply = train_and_generate(site_data)
        await c.message.answer(f"Я изучила материал. Вот что я думаю по этому поводу:\n\n{reply}")
    else:
        await c.message.answer("Не удалось получить данные по ссылке.")

@dp.message()
async def chat_handler(m: types.Message):
    if not m.text: return
    
    # Обучение и ответ
    response = train_and_generate(m.text)
    await m.answer(response)

# ЗАПУСК
async def main():
    # Проверка наличия файла базы
    open(BRAIN_STORAGE, "a").close()
    print("Luum запущена в режиме чистого интеллекта.")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
