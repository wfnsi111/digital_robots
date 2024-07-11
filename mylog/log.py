import os
import logging
from logging import handlers

LOGGING_FMT = '[%(asctime)s]-%(pathname)s-[line:%(lineno)d]-%(levelname)s: %(message)s'

LOGGING_BACKUP_COUNT = 15
LOGGING_INTERVAL = 1
LOGGING_WHEN = 'MIDNIGHT'
LOGGING_NAME = 'robot.log'
LOGGING_DIR = 'log_robot'
LOGGING_SUFFIX = '%Y-%m-%d.log'
LOGGING_LEVEL = logging.DEBUG


# LOGGING_LEVEL = logging.ERROR


def singleton(func):
    __isinstance = {}

    def wrapper(*args, **kwargs):
        if args not in __isinstance:
            __isinstance[func] = func(*args, **kwargs)
        return __isinstance[func]

    return wrapper


@singleton
class Logger:
    def __init__(self, filename=None, level=LOGGING_LEVEL):
        if not filename:
            filename = self._set_dir_()

        self.logger = logging.getLogger(filename)
        format_str = logging.Formatter(LOGGING_FMT, datefmt='%Y-%m-%d %H:%M:%S')
        self.logger.setLevel(level)
        th = handlers.TimedRotatingFileHandler(filename=filename, when=LOGGING_WHEN, interval=LOGGING_INTERVAL,
                                               backupCount=LOGGING_BACKUP_COUNT, encoding='utf-8')
        th.setFormatter(format_str)
        th.suffix = LOGGING_SUFFIX
        self.logger.addHandler(th)

    def _set_dir_(self):
        path = os.path.dirname(os.path.realpath(__file__))
        log_path = os.path.join(path, LOGGING_DIR)

        if not os.path.exists(log_path):
            os.makedirs(log_path)

        logfile = os.path.join(log_path, LOGGING_NAME)
        return logfile


def _get_logger():
    test_logger = Logger()
    return test_logger.logger


logger = _get_logger()

if __name__ == '__main__':
    logger.debug('debug message')
