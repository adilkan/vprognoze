import sqlite3 as sq
from create_bot import bot


def sql_start():
    global base, cur
    base = sq.connect('data.db')
    cur = base.cursor()
    if base:
        print('Data base connected OK!')
    base.execute(
        'CREATE TABLE IF NOT EXISTS configs(result TEXT, percentage INTEGER, odds REAL,id INTEGER PRIMARY KEY AUTOINCREMENT)')
    base.execute(
        'CREATE TABLE IF NOT EXISTS matches(url TEXT UNIQUE)')
    base.commit()


async def sql_add_command(state):
    async with state.proxy() as data:
        cur.execute(f'INSERT INTO configs (result, percentage, odds) VALUES (?, ?, ?)', tuple(data.values()))
        base.commit()


async def sql_remove_command(data):
    id = data.replace('del ', '')
    cur.execute(f'DELETE FROM configs WHERE id == ?', (id,))
    base.commit()


def match_in_database(url):
    check = cur.execute('SELECT * FROM matches WHERE url = ?', (url,)).fetchone()
    return check is not None


def write_match_sql(url):
    cur.execute('INSERT INTO matches (url) VALUES (?)', (url,))
    base.commit()


def get_data():
    return cur.execute('SELECT * FROM configs').fetchall()


def get_data_win():
    return cur.execute('SELECT percentage, odds FROM configs WHERE result = ?', ('Победа',)).fetchall()


def get_data_draw():
    return cur.execute('SELECT percentage, odds FROM configs WHERE result = ?', ('Ничья',)).fetchall()
