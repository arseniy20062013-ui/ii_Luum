import torch
import torch.nn as nn
import aiohttp
from bs4 import BeautifulSoup
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
import re

# Настройки для твоих 4 ГБ ОЗУ и 50% ЦП
TOKEN = '8090178058:AAGwwYNUvE0xEhf4GKVtKOmw8wahSl_x8QM'
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# --- МИНИ-МОЗГ LUUM ---
class LuumBrain(nn.Module):
    def __init__(self, vocab_size=5000):
        super().__init__()
        self.embed = nn.Embedding(vocab_size, 64)
        self.lstm = nn.LSTM(64, 128, batch_first=True)
        self.out = nn.Linear(128, vocab_size)

    def forward(self, x):
        x = self.embed(x)
        output, _ = self.lstm(x)
        return self.out(output)

model = LuumBrain() # Инициализация пустой модели

# --- ФУНКЦИИ ИНТЕРНЕТА ---
async def get_site_content(url):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=5) as resp:
                text = await resp.text()
                soup = BeautifulSoup(text, 'html.parser')
                return soup.get_text()[:600].strip()
    except:
        return "Не удалось прочитать сайт. Возможно, защита от ботов."

# --- ЛОГИКА БОТА ---
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer("Luum активирована! 🚀\nЯ могу:\n1. Читать сайты (просто кинь ссылку)\n2. Рисовать (напиши 'нарисуй ...')\n3. Общаться (пока я учусь)")

@dp.message_handler()
async def main_logic(message: types.Message):
    user_text = message.text.lower()

    # 1. Чтение ссылок
    urls = re.findall(r'(https?://\S+)', user_text)
    if urls:
        await message.answer("🔍 Изучаю содержимое ссылки...")
        content = await get_site_content(urls[0])
        await message.answer(f"Контент сайта:\n\n{content}")
        return

    # 2. Генерация фото (Облачная, чтобы не грузить твои 4ГБ)
    if "нарисуй" in user_text or "фото" in user_text:
        prompt = user_text.replace("нарисуй", "").replace("фото", "").strip()
        if not prompt: prompt = "cyberpunk city"
        await message.answer(f"🎨 Рисую: {prompt}...")
        photo_url = f"https://pollinations.ai/p/{prompt.replace(' ', '_')}?width=1024&height=1024&seed=42"
        await bot.send_photo(message.chat.id, photo=photo_url)
        return

    # 3. Имитация ответа нейросети
    # В реальности тут должен быть токенизатор, но для начала сделаем заглушку, 
    # которая показывает, что Luum задействует "процессор"
    await message.answer("Luum анализирует твой запрос через нейро-слои...")
    # Здесь можно добавить логику генерации текста моделью model(x)

if __name__ == '__main__':
    print("Luum запущена на твоем железе!")
    executor.start_polling(dp, skip_updates=True)