from aiogram.utils import executor
from create_bot import dp, bot
from handlers.client import register_handlers_client
from database.sqlite_db import sql_start
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from parser import main
from keyboards.client_key import kb_client


async def parser():
    users = [691999666, 1311258495]
    data = main()
    for id in users:
        try:
            bot.send_message(id, 'Парсер начал свою работу')
            for i in data:
                first_team, second_team, first, draw, second, url = i
                result = f'{first_team} vs {second_team}\nПобеда 1: {first}\nНичья:      {draw}\nПобеда 2: {second}\n{url}'
                await bot.send_message(id, result)
            if not data:
                await bot.send_message(id, 'Нет матчей подходящих под конфиги')
            await bot.send_message(id, 'Парсер завершил свою работу', reply_markup=kb_client)
        except:
            continue


# scheduler = AsyncIOScheduler()
# scheduler.add_job(parser, 'interval', minutes=5)


async def on_start(_):
    print('Бот начал работу')
    sql_start()
    # scheduler.start()


register_handlers_client(dp)
executor.start_polling(dp, skip_updates=True, on_startup=on_start)
