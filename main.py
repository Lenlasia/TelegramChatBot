import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton
from openai import OpenAI
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import requests

from data import db_session
from data.users import User
from data.requests import Request

client = OpenAI(api_key="sk-proj-6VyJt1wmqrg7Va7WprONT3BlbkFJqz9kJAx3SJqSzYRsOlf8")

storage = MemoryStorage()

# Объект бота
bot = Bot(token="6736833089:AAGhH-jqeNuev9kB-MZzlkB7q2wMi5E-Q2Q")
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


def get_map():
    geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"

    geocoder_params = {
        "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
        "geocode": "Тольятти, Южное Шоссе, 163",
        "format": "json"}

    response = requests.get(geocoder_api_server, params=geocoder_params)

    if not response:
        # обработка ошибочной ситуации
        pass

    # Преобразуем ответ в json-объект
    json_response = response.json()
    # Получаем первый топоним из ответа геокодера.
    toponym = json_response["response"]["GeoObjectCollection"][
        "featureMember"][0]["GeoObject"]
    # Координаты центра топонима:
    toponym_coodrinates = toponym["Point"]["pos"]
    # Долгота и широта:
    toponym_longitude, toponym_lattitude = toponym_coodrinates.split(" ")

    delta = "0.005"

    # Собираем параметры для запроса к StaticMapsAPI:
    map_params = {
        "ll": ",".join([toponym_longitude, toponym_lattitude]),
        "spn": ",".join([delta, delta]),
        "l": "map"
    }

    map_api_server = "http://static-maps.yandex.ru/1.x/"
    # ... и выполняем запрос
    response = requests.get(map_api_server, params=map_params)
    return response.url


@dp.message_handler(commands="start")
async def cmd_test1(message: types.Message):
    db_sess = db_session.create_session()
    if not(db_sess.query(User.tg_id).filter(User.tg_id == message.from_user.id)):
        user = User()
        user.tg_id = message.from_user.id
        user.count_of_used_b = 0
        user.count_of_r = 0
        db_sess.add(user)
    db_sess.commit()
    await message.answer("Здравствуйте! Вас приветствует чат-бот компании ChatBotsManagers.\n\nДля управления ботом "
                         "воспользуйтесь меню снизу. Также чтобы узнать подробнее возпользуйтесь командой /help", reply_markup=keyboard)


@dp.message_handler(commands="help")
async def cmd_test1(message: types.Message):
    await message.answer("Здравствуйте! Вас приветствует чат-бот компании ChatBotsManagers.\n\nДля управления ботом "
                         "воспользуйтесь меню снизу. Наш чат-бот поможет вам получить информацию об"
                         "услугах компании, её портфолио и команде, а также вы сможете оставить запрос"
                         "на обратную связь и связаться с менеджером в реальном времени!\nПриятного пользования!", reply_markup=keyboard)


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


@dp.message_handler(content_types=types.ContentType.PHOTO)
async def handle_photo(message: types.Message):
    # Получаем информацию о фотографии
    photo = message.photo[-1]  # Берем самую последнюю (самую большую) фотографию
    file_id = photo.file_id

    # Отправляем фотографию обратно с сообщением
    await bot.send_photo(message.chat.id, file_id, caption="Вот ваша фотография! Любуйтесь ей также, как вы можете "
                                                           "любоваться нашими проектами, сделанными для вас! С "
                                                           "уважением, ChatBotManagers")


@dp.message_handler()
async def cmd_test1(message: types.Message):
    db_sess = db_session.create_session()
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
            user = db_sess.query(User).filter(User.tg_id == message.from_user.id).first()
            user.count_of_used_b += 1
            db_sess.commit()
            del open_tickets[open_tickets.index(message.chat.id)]
            await message.answer('Ваш тикет был закрыт!', reply_markup=keyboard)
            await bot.send_message(-1001722492789, f'Тикет {message.chat.id} был закрыт пользователем!')
        elif message.chat.id in open_tickets:
            await bot.send_message(-1001722492789, f"Ticket - {message.chat.id}\n\n{message.text}")
        elif message.text == 'О компании 🏢':
            user = db_sess.query(User).filter(User.tg_id == message.from_user.id).first()
            user.count_of_used_b += 1
            db_sess.commit()
            if 'group' in message.chat.type:
                await message.answer('Перейдите в чат с ботом, для дальнейшего использования команд.')
                return
            await message.answer(
                "ChatBotsManagers — ведущая компания в области разработки web-продуктов и чат-ботов, которая сочетает "
                "в себе инновационные технологии с глубоким пониманием потребностей клиентов. Мы стремимся к тому, "
                "чтобы каждый наш проект был уникальным, функциональным и эффективным инструментом для наших "
                "клиентов.\n\nНаша Миссия:\n\nМы стремимся к тому, чтобы сделать технологии доступными и полезными "
                "для каждого бизнеса. Наша миссия - создавать инновационные и интуитивно понятные продукты, "
                "которые помогают нашим клиентам улучшать свои бизнес-процессы и обеспечивать высокий уровень "
                "обслуживания своих клиентов.\n\nНаши Услуги:\n\nРазработка Web-продуктов: Мы создаем современные, "
                "отзывчивые и функциональные веб-приложения, которые соответствуют потребностям и целям наших "
                "клиентов.\n\nЧат-боты: Наши чат-боты основаны на передовых технологиях и способны автоматизировать "
                "коммуникацию с клиентами, улучшая сервис и оптимизируя бизнес-процессы.\n\nКонсалтинг и Поддержка: "
                "Мы предоставляем консультационную поддержку наших клиентов на всех этапах проекта, начиная с анализа "
                "потребностей и заканчивая внедрением и поддержкой готового продукта.\n\nНаш Подход:\n\nМы ценим "
                "индивидуальный подход к каждому проекту и каждому клиенту. Наша команда состоит из опытных "
                "специалистов, готовых реализовать даже самые амбициозные идеи. Мы стремимся к постоянному развитию и "
                "обновлению наших навыков и знаний, чтобы быть в курсе последних технологических трендов и лучших "
                "практик в области разработки.\n\nПочему ChatBotsManagers:\n\nОпыт: Наша команда имеет богатый опыт в "
                "разработке и внедрении различных web-продуктов и чат-ботов.\n\nИндивидуальный Подход: Мы учитываем "
                "уникальные потребности каждого клиента и разрабатываем решения, которые соответствуют их целям и "
                "задачам.\n\nИнновации и Технологии: Мы следим за последними технологическими трендами и используем "
                "передовые технологии в наших проектах.\n\nПрисоединяйтесь к ChatBotsManagers сегодня, "
                "и давайте вместе создадим продукты, которые изменят ваш бизнес к лучшему!")
            await bot.send_photo(chat_id=message.chat.id, photo=get_map(), caption="Наш офис на Карте!")
        elif message.text == 'Команда👨‍👦‍👦':
            user = db_sess.query(User).filter(User.tg_id == message.from_user.id).first()
            user.count_of_used_b += 1
            db_sess.commit()
            if 'group' in message.chat.type:
                await message.answer('Перейдите в чат с ботом, для дальнейшего использования команд.')
                return
            await message.answer('Егор Маликов - Программист, умение работать с Python, фреймворками Flask. Наличие '
                                 'технической грамотности, коммуникационных навыков, аналитического мышления и '
                                 'стремления к совершеннству.\n"Усидчивость и грамотность - одни из самых важных '
                                 'качеств для программиста"\n\nЕгор Маркачев - программист, FullStack-разработчик. '
                                 'Опыт работы с Django, Flask, SQlite, PostgreSQL. Огромный опыт в разработке '
                                 'WEB-продуктов и чат-ботов.\n"Никогда нельзя останавливаться на достигнутом, '
                                 'нужно стремится к совершенству!"')
        elif message.text == 'Стоимость 💵':
            user = db_sess.query(User).filter(User.tg_id == message.from_user.id).first()
            user.count_of_used_b += 1
            db_sess.commit()
            if 'group' in message.chat.type:
                await message.answer('Перейдите в чат с ботом, для дальнейшего использования команд.')
                return
            await message.answer(
                "Цена на готовый продукт зависит от технического задания."
                "\n\nРазработка сайтов - от 50.00₽\n\nSEO-оптимизация - от 50.00₽\n\nРазработка бота - от "
                "10.000₽\n\nРазработка "
                "приложений для дополненой реальности - от 100.00₽\n\nРазработка приложений для "
                "виртуальной реальности - от 100.00₽\n\nПрикладное применение нейросетей и их "
                "интеграция в различные решения индустрии информационнных технологий - от 300.00₽")
        elif message.text == 'Портфолио 💼':
            user = db_sess.query(User).filter(User.tg_id == message.from_user.id).first()
            user.count_of_used_b += 1
            db_sess.commit()
            if 'group' in message.chat.type:
                await message.answer('Перейдите в чат с ботом, для дальнейшего использования команд.')
                return
            await message.answer('Снизу представлены наши крупные проекты. Вы можете протестировать каждый из них и '
                                 'посмотреть, как устроены наши проекты и насколько хорошо наша команда выполняет '
                                 'свою работу!', reply_markup=portfolio)
        elif message.text == 'Связаться с менеджером 👩‍💼':
            user = db_sess.query(User).filter(User.tg_id == message.from_user.id).first()
            user.count_of_used_b += 1
            db_sess.commit()
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
            user = db_sess.query(User).filter(User.tg_id == message.from_user.id).first()
            user.count_of_r += 1

            req = Request()
            user.requests.append(req)
            
            db_sess.commit()
            if 'group' in message.chat.type:
                await message.answer('Перейдите в чат с ботом, для дальнейшего использования команд.')
                return
            await message.answer('Укажите способ, как с Вами связаться (Номер телефона, ID Telegram и т.д.).',
                                 reply_markup=ReplyKeyboardMarkup().add('Отменить❌'))
            await FormObratSvyaz.sposob.set()
        elif message.text == 'Обратится к ChatGPT':
            user = db_sess.query(User).filter(User.tg_id == message.from_user.id).first()
            user.count_of_used_b += 1
            db_sess.commit()
            if 'group' in message.chat.type:
                await message.answer('Перейдите в чат с ботом, для дальнейшего использования команд. @AlViRityGPT_bot')
                return
            await message.answer('Напишите ваш запрос к ChatGPT',
                                 reply_markup=ReplyKeyboardMarkup().add('Завершить диалог с ChatGPT'))
            await FormGPT.zapros.set()
        else:
            if message.chat.type == 'private':
                prompt = f'Представь, ' \
                         f'что ты чат-бот компании по разработке WEB-сайтов, ботов, AR/VR и мобильных приложений, ' \
                         f'а также ' \
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
    db_session.global_init("db/db.sqlite")
    executor.start_polling(dp, skip_updates=True)

