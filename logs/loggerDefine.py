import logging
from logging import handlers

import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


def loggerDefine(loggerFile):
    strDefaultFormatter = '%(asctime)s|%(processName)s|%(threadName)s|%(levelname)s|%(filename)s:%(lineno)d|%(funcName)s|%(message)s'
    objRotatingHandler = handlers.TimedRotatingFileHandler(loggerFile, when='MIDNIGHT', delay=True,
                                                           backupCount=9)
    objFormatter = logging.Formatter(strDefaultFormatter)
    objRotatingHandler.setFormatter(objFormatter)
    logging.getLogger().addHandler(objRotatingHandler)
    logging.getLogger().propagate = False
    objConsoleHandler = logging.StreamHandler()
    objConsoleHandler.setFormatter(objFormatter)
    logging.getLogger().addHandler(objConsoleHandler)
    logging.getLogger().setLevel(logging.INFO)
    logging.getLogger("requests").setLevel(logging.NOTSET)
    logging.getLogger("urllib3").setLevel(logging.NOTSET)
    return logging
