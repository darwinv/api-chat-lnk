import logging.handlers
import sys, os, platform
from linkupapi.settings import LOGGER_CONFIG


def setup_log(log_name):
    LOGGER_NAME = log_name
    LOG_FOLDER = LOGGER_CONFIG['log_foler']
    LOG_FILE = LOGGER_CONFIG['files'][log_name] if log_name in LOGGER_CONFIG['files'] else LOGGER_CONFIG['files']['error-dev']
    ROTATE_TIME = LOGGER_CONFIG['rotate_time']
    LOG_LEVEL = LOGGER_CONFIG['log_level']
    LOG_COUNT = LOGGER_CONFIG['log_count']
    LOG_FORMAT = LOGGER_CONFIG['log_format']
    LOG_MAXSIZE = LOGGER_CONFIG['log_maxsize']
    LOG_MODE = LOGGER_CONFIG['log_mode']

    if platform.platform().startswith('Windows'):
        FILE_PATH = os.path.join(os.getenv('HOMEDRIVE'),
                                 os.getenv("HOMEPATH"),
                                 LOG_FOLDER,
                                 LOG_FILE)
    else:
        FILE_PATH = os.path.join(os.getenv('HOME'), '~', LOG_FOLDER, 'LOG_FILE')

    try:
        logger = logging.getLogger(LOGGER_NAME)
        # loggerHandler = logging.basicConfig(filename=FILE_PATH, filemode="a", format=LOG_FORMAT, level=LOG_LEVEL)
        loggerHandler = logging.handlers.RotatingFileHandler(FILE_PATH, mode=LOG_MODE, maxBytes=LOG_MAXSIZE,
                                                             backupCount=LOG_COUNT, encoding=None, delay=0)
        # loggerHandler = logging.handlers.TimedRotatingFileHandler(FILE_PATH, ROTATE_TIME, 1, backupCount=LOG_COUNT)
        formatter = logging.Formatter(LOG_FORMAT)
        loggerHandler.setFormatter(formatter)
        logger.addHandler(loggerHandler)
        logger.setLevel(LOG_LEVEL)
        return logger
    except Exception as error:
        print("Error with logs: %s" % (str(error)))
        sys.exit()

# def getLogger():
#     return logger
# loggerMesage.critical('critical message')
# loggerMesage.debug('debug message')
# loggerMesage.exception("error")
