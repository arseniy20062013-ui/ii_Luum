import asyncio
import aiohttp
import random
import re
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from bs4 import BeautifulSoup

# КОНФИГ
TOKEN = "8090178058:AAGwwYNUvE0xEhf4GKVtKOmw8wahSl_x8QM"
bot = Bot(token=TOKEN)
dp = Dispatcher()

# УНИВЕРСАЛЬНЫЙ СЛОВАРЬ (САМООБУЧАЮЩИЙСЯ)
# Структура: { 'язык': { 'слово': ['следующее_слово'] } }
brain = {
    "ru": {"привет": ["как", "дела"], "что": ["ты", "делаешь"], "кто": ["ты"]},
    "en": {"hello": ["how", "are"], "what": ["is", "up"], "who": ["are"]},
    "es": {"hola": ["como", "estas"], "que": ["tal"]},
    "zh": {"你好": ["吗"], "你是": ["谁"]}
}

STORAGE = "universal_brain.txt"

# ОПРЕДЕЛЕНИЕ ЯЗЫКА (Детектор букв)
def detect_lang(text):
    if re.search(r'[а-яА-Я]', text): return "ru"
    if re.search(r'[a-zA-Z]', text): return "en"
    if re.search(r'[\u4e00-\u9fff]', text): return "zh"
    return "en"

# ОБУЧЕНИЕ (Запись фраз и связей в мозг)
def learn(text):
    lang = detect_lang(text)
    if lang not in brain: brain[lang] = {}
    
    words = re.findall(r'\w+', text.lower())
    for i in range(len(words) - 1):
        curr, nxt = words[i], words[i+1]
        if curr not in brain[lang]: brain[lang][curr] = []
        brain[lang][curr].append(nxt)
    
    with open(STORAGE, "a", encoding="utf-8") as f:
        f.write(f"{lang}|{text}\n")

# ГЕНЕРАЦИЯ ОТВЕТА (Мышление Luum)
def think(text):
    lang = detect_lang(text)
    words = re.findall(r'\w+', text.lower())
    
    if not words or lang not in brain:
        return "..."

    # Берем последнее слово как зацепку для начала мысли
    seed = words[-1]
    if seed not in brain[lang]:
        # Если слово новое, берем случайное из этого языка
        seed = random.choice(list(brain[lang].keys()))
    
    response = [seed]
    # Генерируем цепочку до 12 слов
    curr = seed
    for _ in range(12):
        if curr in brain[lang] and brain[lang][curr]:
            nxt = random.choice(brain[lang][curr])
            response.append(nxt)
            curr = nxt
        else:
            break
            
    return " ".join(response).capitalize()

# ЗАГРУЗКА БАЗЫ
def load_data():
    try:
        with open(STORAGE, "r", encoding="utf-8") as f:
            for line in f:
                if "|" in line:
                    _, txt = line.split("|", 1)
                    learn(txt.strip())
    except FileNotFoundError:
        open(STORAGE, "w").close()

# ПАРСЕР
async def get_site_content(url):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as r:
                s = BeautifulSoup(await r.text(), 'html.parser')
                return s.get_text()
    except: return None

@dp.message(Command("start"))
async def start(m: types.Message):
    await m.answer(
        "Luum Online.\n\n"
        "Языковое ядро загружено. Я понимаю структуру RU, EN, ES, ZH.\n"
        "Я обучаюсь на каждом твоем предложении и на лету строю ответ на твоем языке."
    )

@dp.message(F.text)
async def handle_msg(m: types.Message):
    # Если это ссылка — обучаемся на сайте
    urls = re.findall(r'(https?://\S+)', m.text)
    if urls:
        await m.answer("Впитываю новые языковые структуры с сайта...")
        content = await get_site_content(urls[0])
        if content: 
            learn(content)
            return await m.answer("Языковая база обновлена.")

    # Обычное общение
    learn(m.text) # Сначала учим то, что сказал юзер
    response = think(m.text) # Потом генерируем ответ
    await m.answer(response)

async def main():
    load_data()
    print("Luum Brain: Обучение завершено. Бот готов.")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
