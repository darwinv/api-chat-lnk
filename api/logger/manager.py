import logging.handlers
import logging
import sys, os, platform
from linkupapi.settings import LOGGER_CONFIG

# Ussage ############################# 
# from api.logger import manager
# logger = manager.setup_log(__name__)
# logger.info("id de categoria: ")

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
        FOLDER_PATH = os.path.join(os.getenv('HOMEDRIVE'),
                                 os.getenv("HOMEPATH"),
                                 LOG_FOLDER)

    else:
        FILE_PATH = os.path.join(os.getenv('HOME'), LOG_FOLDER, LOG_FILE)
        FOLDER_PATH = os.path.join(os.getenv('HOME'), LOG_FOLDER)


    try:
        logger = logging.getLogger(LOGGER_NAME)
        
        if not os.path.exists(FOLDER_PATH):
            os.makedirs(FOLDER_PATH)
        
        # loggerHandler = logging.basicConfig(filename=FILE_PATH, filemode="a", format=LOG_FORMAT, level=LOG_LEVEL)
        loggerHandler = logging.handlers.RotatingFileHandler(FILE_PATH, mode=LOG_MODE, maxBytes=LOG_MAXSIZE,
                                                             backupCount=LOG_COUNT, encoding=None, delay=0)
        # loggerHandler = logging.handlers.TimedRotatingFileHandler(FILE_PATH, ROTATE_TIME, 1, backupCount=LOG_COUNT)
        
        formatter = logging.Formatter(LOG_FORMAT)
        loggerHandler.setFormatter(formatter)
        logger.addHandler(loggerHandler)
        logger.setLevel(LOG_LEVEL)

        f = ContextFilter()
        logger.addFilter(f)

        return logger
    except Exception as error:
        print("Error with logs: %s" % (str(error)))
        sys.exit()

class ContextFilter(logging.Filter):
    """
    This is a filter which injects contextual information into the log.
    """

    def filter(self, record):
        # record.ip = self.get_client_ip(request)
        record.ip = '127.0.0.1'
        return True

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def get_ip(self):
        return ""
        # return jsonify(request.remote_addr), 200
        