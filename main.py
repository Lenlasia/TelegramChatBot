import logging
from aiogram import Bot, Dispatcher, executor, types

# Устанавливаем уровень логирования
logging.basicConfig(level=logging.INFO)

# Инициализируем бота
API_TOKEN = '6521745200:AAGgNSMHE8Pm4WNodawoyRB9xSzZNrw6Q3o'
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Обработка команды /start
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply("Привет! Я чат-бот. Как я могу помочь тебе?")

# Обработка всех остальных сообщений
@dp.message_handler()
async def echo(message: types.Message):
    await message.reply(f"Вы сказали: {message.text}")

# Запускаем бота
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
