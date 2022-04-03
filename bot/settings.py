import logging.config
import os.path
import utils

dir_path = os.path.dirname(__file__)[:-4]

FILENAME = f'{dir_path}/log/bot.log'

if os.path.isdir('/var/log/damask/misc'):
    LOG_PATH = '/var/log/damask/misc/{}'.format(FILENAME)
else:
    LOG_PATH = FILENAME

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,

    'formatters': {
        'default_formatter': {
            'format': '[%(asctime)s][%(levelname)s] - %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
    },

    'handlers': {
        'stream_handler': {
            'class': 'logging.StreamHandler',
            'formatter': 'default_formatter',
        },
        'info_rotating_file_handler': {
            'level': 'INFO',
            'formatter': 'default_formatter',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOG_PATH,
            'mode': 'a',
            'maxBytes': 1048576,
            'backupCount': 10
        },
    },

    'loggers': {
        'bot': {
            'handlers': ['stream_handler', 'info_rotating_file_handler'],
            'level': 'INFO',
            'propagate': False
        }
    }
}

logging.config.dictConfig(LOGGING_CONFIG)

DB_PATH = f'{dir_path}/db.sqlite3' if os.path.isfile('/opt/TelegramPdfBot/db.sqlite3') else utils.init_database(dir_path)
TOKEN = '1429399583:AAH76Aqvx545ygGpM08J7Wr1XBq_2AJsH7E'