from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

storage = MemoryStorage()
bot = Bot(token='6187716780:AAFQlFknIJ55MBRaUT7_lu3fZAGsC5-Zpk4')
dp = Dispatcher(bot, storage=storage)
