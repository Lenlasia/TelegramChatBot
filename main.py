import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton
from openai import OpenAI

client = OpenAI(api_key="")
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage

storage = MemoryStorage()

# Объект бота
bot = Bot(token="")
# Диспетчер для бота
dp = Dispatcher(bot, storage=storage)
# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)

open_tickets = []
supports = [1624709653, 1062104473]

engine = "gpt-3.5-turbo"

keyboard = ReplyKeyboardMarkup().add(KeyboardButton(text="О компании 🏢")).add(
    KeyboardButton(text="Команда👨‍👦‍👦")).add(KeyboardButton(text="Стоимость 💵")).add(
    KeyboardButton(text="Портфолио 💼")).add(KeyboardButton(text="Связаться с менеджером 👩‍💼")).add(
    KeyboardButton(text='Обратная связь 📞')).add(KeyboardButton(text='Обратится к ChatGPT'))

portfolio = InlineKeyboardMarkup().add()

adminkeyboard = ReplyKeyboardMarkup().add(KeyboardButton(text='Текст "О компании"')).add(
    KeyboardButton(text='Текст "Команда"')).add(KeyboardButton(text='Текст "Стоимость"')).add(
    KeyboardButton(text='Экстренное выключение бота'))


class FormObratSvyaz(StatesGroup):
    sposob = State()
    name = State()
    vremya = State()


class FormGPT(StatesGroup):
    zapros = State()


@dp.message_handler(commands="start")
async def cmd_test1(message: types.Message):
    await message.answer("Здравствуйте! Вас приветствует чат-бот компании .\n\nДля управления ботом "
                         "воспользуйтесь меню снизу.", reply_markup=keyboard)


@dp.message_handler(state=FormObratSvyaz.sposob)
async def enter_volume(message: types.Message, state: FSMContext):
    answer = message.text
    if answer == 'Отменить❌':
        await message.answer('Форма была закрыта!', reply_markup=keyboard)
        await state.finish()
        return
    await state.update_data(answer1=answer)
    await message.answer('Как к Вам можно обращатся?')
    await FormObratSvyaz.name.set()


@dp.message_handler(state=FormObratSvyaz.name)
async def enter_volume(message: types.Message, state: FSMContext):
    answer = message.text
    if answer == 'Отменить❌':
        await message.answer('Форма была закрыта!', reply_markup=keyboard)
        await state.finish()
        return
    await state.update_data(answer2=answer)
    await message.answer('В какое время можно с Вами связаться?')
    await FormObratSvyaz.vremya.set()


@dp.message_handler(state=FormObratSvyaz.vremya)
async def enter_volume(message: types.Message, state: FSMContext):
    answer = message.text
    await state.update_data(answer3=answer)
    await message.answer('В ближайшее время свяжемся с Вами! Спасибо за проявленный интерес.', reply_markup=keyboard)
    sposob = (await state.get_data())['answer1']
    name = (await state.get_data())['answer2']
    await bot.send_message(-1001722492789,
                           f'Новая заявка на обратную связь.\nСпособ связи - {sposob}\nИмя - {name}.\nЖелаемое время - {answer}')
    await state.finish()


@dp.message_handler(state=FormGPT)
async def enter_volume(message: types.Message, state: FSMContext):
    answer = message.text
    if answer == 'Завершить диалог с ChatGPT':
        await message.answer('Для дальнейшего использования бота, используйте меню ниже.', reply_markup=keyboard)
        await state.finish()
        return
    completion = client.chat.completions.create(model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": answer}])
    await message.answer(completion.choices[0].message.content)
    await FormGPT.zapros.set()



@dp.message_handler()
async def cmd_test1(message: types.Message):
    if message.chat.id == -1001722492789:
        if '/close_ticket' in message.text:
            mess = message.text.replace('/close_ticket ', '')
            if int(mess) in open_tickets:
                del open_tickets[open_tickets.index(int(mess))]
                await message.answer(f'Тикет {mess} был закрыт')
                await bot.send_message(int(mess), f'Ваш тикет был закрыт!', reply_markup=keyboard)
            else:
                await message.answer('Тикет не существует!')
        elif '/answer' in message.text:
            mess = message.text.replace('/answer ', '').split(" ", 1)
            if int(mess[0]) in open_tickets:
                await bot.send_message(int(mess[0]), mess[1])
            else:
                await message.answer('Тикет не существует!')
        elif '/admin' in message.text:
            await message.answer('Приветствуем в админ-панели.\n\nЧто хотите поменять?')
    else:
        if message.text == 'Отменить❌' and message.chat.id in open_tickets:
            del open_tickets[open_tickets.index(message.chat.id)]
            await message.answer('Ваш тикет был закрыт!', reply_markup=keyboard)
            await bot.send_message(-1001722492789, f'Тикет {message.chat.id} был закрыт пользователем!')
        elif message.chat.id in open_tickets:
            await bot.send_message(-1001722492789, f"Ticket - {message.chat.id}\n\n{message.text}")
        elif message.text == 'О компании 🏢':
            if 'group' in message.chat.type:
                await message.answer('Перейдите в чат с ботом, для дальнейшего использования команд.')
                return
            await message.answer('')
        elif message.text == 'Команда👨‍👦‍👦':
            if 'group' in message.chat.type:
                await message.answer('Перейдите в чат с ботом, для дальнейшего использования команд.')
                return
            await message.answer('')
        elif message.text == 'Стоимость 💵':
            if 'group' in message.chat.type:
                await message.answer('Перейдите в чат с ботом, для дальнейшего использования команд.')
                return
            await message.answer(
                'Цена на готовый продукт зависит от технического задания.'
                '\n\nРазработка сайтов - от 50.000₽\n\nSEO-оптимизация - от 50.000₽\n\nРазработка бота - от '
                '10.000₽\n\nРазработка '
                'приложений для дополненой реальности - от 100.000₽\n\nРазработка приложений для '
                'виртуальной реальности - от 100.000₽\n\nПрикладное применение нейросетей и их '
                'интеграция в различные решения индустрии информационнных технологий - от 300.000₽')
        elif message.text == 'Портфолио 💼':
            if 'group' in message.chat.type:
                await message.answer('Перейдите в чат с ботом, для дальнейшего использования команд.')
                return
            await message.answer('Снизу представлены наши крупные проекты.\nОстальные проекты вы можете найти в нашей '
                                 'группе ВК.', reply_markup=portfolio)
        elif message.text == 'Связаться с менеджером 👩‍💼':
            if 'group' in message.chat.type:
                await message.answer('Перейдите в чат с ботом, для дальнейшего использования команд.')
                return
            await message.answer(
                'Менеджер, освободившийся в близжайшее время ответит Вам. Напишите ваше обращение в чате с ботом.',
                reply_markup=ReplyKeyboardMarkup().add('Отменить❌'))
            open_tickets.append(message.chat.id)
            await bot.send_message(-1001722492789,
                                   f'Открыт новый тикет!\n\nНомер: {message.chat.id}\n\nДля закрытия тикета напишите:\n/close_ticket {message.chat.id}\nДля ответа на сообщение пользователя - /answer {message.chat.id}')
        elif message.text == 'Обратная связь 📞':
            if 'group' in message.chat.type:


                await message.answer('Перейдите в чат с ботом, для дальнейшего использования команд.')
                return
            await message.answer('Укажите способ, как с Вами связаться (Номер телефона, ID Telegram и т.д.).',
                                 reply_markup=ReplyKeyboardMarkup().add('Отменить❌'))
            await FormObratSvyaz.sposob.set()
        elif message.text == 'Обратится к ChatGPT':
            if 'group' in message.chat.type:
                await message.answer('Перейдите в чат с ботом, для дальнейшего использования команд. @AlViRityGPT_bot')
                return
            await message.answer('Напишите ваш запрос к ChatGPT',
                                 reply_markup=ReplyKeyboardMarkup().add('Завершить диалог с ChatGPT'))
            await FormGPT.zapros.set()
        else:
            if message.chat.type == 'private':
                prompt = f'Представь, что ты чат-бот компании по разработке WEB-сайтов, ботов, AR/VR и мобильных приложений, а также ' \
                         f'интеграцией нейронных сетей в различные решения индустрии информационных технологий! ' \
                         f'Пользователь напис' \
                         f'ал тебе: {message.text}, ответь ему пожалуйста.'
                completion = client.chat.completions.create(model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}])
                await message.answer('Ответ Нейросети:')
                await message.answer(completion.choices[0].message.content)
                await message.answer('Для дальнейшего использования бота, используйте меню ниже.',
                                     reply_markup=keyboard)


if __name__ == "__main__":
    # Запуск бота
    executor.start_polling(dp, skip_updates=True)
