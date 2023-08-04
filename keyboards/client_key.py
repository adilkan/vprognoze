from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


new = KeyboardButton('/New_Config')
list_of_configs = KeyboardButton('/Config_List')
parser = KeyboardButton('/Parser')

kb_client = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
kb_client.row(new, list_of_configs).add(parser)

win = KeyboardButton('Победа')
draw = KeyboardButton('Ничья')

choose_variant = ReplyKeyboardMarkup(resize_keyboard=True,one_time_keyboard=True)
choose_variant.row(win, draw)


yes = KeyboardButton('Да✅')
no = KeyboardButton('Нет❌')
answer = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
answer.row(yes, no)


