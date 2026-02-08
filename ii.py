import asyncio
import aiohttp
import random
import re
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from bs4 import BeautifulSoup

# КОНФИГ
TOKEN = "8090178058:AAGwwYNUvE0xEhf4GKVtKOmw8wahSl_x8QM"
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Глобальный словарь Luum (Мозг в ОЗУ)
# Здесь будут храниться связи между буквами и словами всех языков
luum_brain = {}

# Файл для сохранения опыта на диск (80ГБ памяти позволяют хранить всё)
BRAIN_STORAGE = "luum_universal_brain.txt"

# Функция для обучения на лету
def learn_text(text):
    words = text.split()
    for i in range(len(words) - 1):
        current_word = words[i]
        next_word = words[i+1]
        if current_word not in luum_brain:
            luum_brain[current_word] = []
        luum_brain[current_word].append(next_word)
    
    with open(BRAIN_STORAGE, "a", encoding="utf-8") as f:
        f.write(text + " ")

# Функция генерации (Мышление)
def generate_response(seed_text):
    input_words = seed_text.split()
    if not input_words:
        return "Система ожидает ввод..."
    
    # Пытаемся зацепиться за последнее слово пользователя
    current_word = input_words[-1]
    response = []
    
    # Генерируем цепочку до 15 слов
    for _ in range(15):
        if current_word in luum_brain:
            next_word = random.choice(luum_brain[current_word])
            response.append(next_word)
            current_word = next_word
        else:
            break
            
    if not response:
        # Если Luum не знает этого слова, она пробует собрать фразу из случайных известных
        if luum_brain:
            random_key = random.choice(list(luum_brain.keys()))
            return f"Я изучаю слово '{seed_text}'. Мой текущий уровень понимания говорит: {random_key}..."
        return "Мой словарь пуст. Продолжай писать, я впитываю каждое слово."
        
    return " ".join(response)

# Загрузка базы при старте
def load_brain():
    try:
        with open(BRAIN_STORAGE, "r", encoding="utf-8") as f:
            data = f.read()
            if data:
                learn_text(data)
                print(f"Загружено связей: {len(luum_brain)}")
    except FileNotFoundError:
        open(BRAIN_STORAGE, "w").close()

# ПАРСЕР
async def learn_from_site(url):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as resp:
                soup = BeautifulSoup(await resp.text(), 'html.parser')
                for tag in soup(["script", "style", "nav", "footer"]): tag.decompose()
                return " ".join(soup.get_text().split())
    except: return None

# ОБРАБОТЧИКИ
@dp.message(Command("start"))
async def cmd_start(m: types.Message):
    await m.answer(
        "Luum активирована.\n\n"
        "Я — самообучающийся языковой движок. Я не использую чужие API. "
        "Мой мозг пуст в начале, но я запоминаю каждое слово, букву и символ на любом языке. "
        "Пиши мне, и я начну имитировать твою речь и думать самостоятельно."
    )

@dp.message(F.text.regexp(r'(https?://\S+)'))
async def handle_link(m: types.Message):
    url = re.findall(r'(https?://\S+)', m.text)[0]
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Поглотить текст", callback_data=f"L|{url}")]])
    await m.answer("Вижу источник данных. Добавить его в мой словарь?", reply_markup=kb)

@dp.callback_query(F.data.startswith("L|"))
async def process_learning(c: types.CallbackQuery):
    url = c.data.split("|")[1]
    await c.answer("Впитываю знания...")
    data = await learn_from_site(url)
    if data:
        learn_text(data)
        await c.message.answer("Текст сайта успешно добавлен в мой словарь. Теперь я знаю больше слов.")
    else:
        await c.message.answer("Не удалось получить доступ к тексту.")

@dp.message()
async def chat(m: types.Message):
    if not m.text: return
    
    user_text = m.text
    # Обучаемся на входящем сообщении
    learn_text(user_text)
    
    # Думаем и отвечаем
    response = generate_response(user_text)
    await m.answer(response)

# ЗАПУСК
async def main():
    load_brain()
    print("Сервер Luum запущен.")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
