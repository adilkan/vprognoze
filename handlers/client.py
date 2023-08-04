from aiogram import types
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from create_bot import bot
from keyboards import client_key
from database.sqlite_db import sql_add_command, get_data, sql_remove_command
from parser import main


async def start(message: types.Message):
    await bot.send_message(message.chat.id, 'Здравствуйте, это бот для парсинга', reply_markup=client_key.kb_client)


class FSMClient(StatesGroup):
    choose = State()
    percentage = State()
    odds = State()
    check = State()


async def cm_start(message: types.Message):
    await FSMClient.choose.set()
    await bot.send_message(message.chat.id, 'Выберите исход матча: ', reply_markup=client_key.choose_variant)


async def choose(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['choose'] = message.text
    await FSMClient.next()
    await bot.send_message(message.chat.id, 'Отправьте процент\nПример: 21')


async def percentage(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        result = message.text
        result = result.replace('%', '')
        try:
            data['procentage'] = int(result)
        except ValueError:
            await bot.send_message(message.chat.id, 'Вы ввели не число. Введите число еще раз:')
            return
    await FSMClient.next()
    await bot.send_message(message.chat.id, 'Отправьте коэффициент\nПример: 3.23 или 3')


async def odds(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        result = message.text
        result = result.replace(',', '.')
        try:
            data['odds'] = float(result)
        except ValueError:
            await bot.send_message(message.chat.id, 'Вы ввели не число. Введите число еще раз:')
            return
    result = ''
    for val, key in zip(data.values(), ['Исход матча', 'Процент', 'Коэффициент']):
        result += f'{key} : {val}\n'
    await bot.send_message(message.chat.id, result)
    await FSMClient.next()
    await bot.send_message(message.chat.id, 'Все верно ?', reply_markup=client_key.answer)


async def check(message: types.Message, state: FSMContext):
    if message.text == 'Да✅':
        await bot.send_message(message.chat.id, 'Бот добавил новую конфигурацию✅', reply_markup=client_key.kb_client)
        await sql_add_command(state)
    else:
        await bot.send_message(message.chat.id, 'Новая конфигурация не добавлена❌', reply_markup=client_key.kb_client)
    await state.finish()


async def callback_run(callback_query: types.CallbackQuery):
    await sql_remove_command(callback_query.data)
    await callback_query.answer(text=f'Конфигурация удаленна')


async def get_configs(message: types.Message):
    data = get_data()
    for i in data:
        result = f'Результат: {i[0]}\n' \
                 f'Процент: {i[1]}%\n' \
                 f'Коэффициент: {i[2]}'
        button = InlineKeyboardMarkup()
        button.add(InlineKeyboardButton('Удалить', callback_data=f'del {i[3]}'))
        await bot.send_message(message.chat.id, result, reply_markup=button)

    if not data:
        await bot.send_message(message.chat.id, 'Список конфигов пуст')
    await bot.send_message(message.chat.id, 'Что хотите хозяин ?', reply_markup=client_key.kb_client)


async def parser(message):
    await bot.send_message(message.chat.id, 'Парсер начал свою работу')
    data = main()
    for i in data:
        first_team, second_team, first, draw, second, url = i
        result = f'{first_team} vs {second_team}\nПобеда 1: {first}\nНичья:      {draw}\nПобеда 2: {second}\n{url}'
        await bot.send_message(message.chat.id, result)
    if not data:
        await bot.send_message(message.chat.id, 'Нет матчей подходящих под конфиги')
    await bot.send_message(message.chat.id, 'Парсер завершил свою работу', reply_markup=client_key.kb_client)


def register_handlers_client(dp: Dispatcher):
    dp.register_message_handler(start, commands='start', state=None)
    dp.register_message_handler(cm_start, commands='New_Config')
    dp.register_message_handler(choose, state=FSMClient.choose)
    dp.register_message_handler(percentage, state=FSMClient.percentage)
    dp.register_message_handler(odds, state=FSMClient.odds)
    dp.register_message_handler(check, state=FSMClient.check)
    dp.register_message_handler(get_configs, commands='Config_List')
    dp.register_callback_query_handler(callback_run, lambda x: x.data.startswith('del'))
    dp.register_message_handler(parser, commands='Parser')
