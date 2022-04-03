import datetime
import logging
import os.path
import sqlite3
from pathlib import Path

logger = logging.getLogger('bot')


def time():
    date = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=5.0))).strftime("%Y-%m-%d %H:%M:%S")
    return date


def init_database(dir_path):
    commands = []
    db_dir = f'{dir_path}/DB'
    files = list(map(str, Path(db_dir).glob('*.sql')))

    for file in files:
        with open(file, 'r') as f:
            commands += [i.strip() for i in f.read().split(';')]

    con = sqlite3.connect(dir_path + '/db.sqlite3')
    cur = con.cursor()
    for command in commands:
        try:
            cur.execute(command)
            logger.info(f'Success command [{command.splitlines()[0]}]')
        except sqlite3.Error as e:
            logger.warning(f'{e}, command = {command}')
        except Exception as e:
            logger.error(e)
    return dir_path+'/db.sqlite3'
