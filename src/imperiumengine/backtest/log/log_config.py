# -*- coding: utf-8 -*-

"""
~~~~~~~~~~~~
Apr, 2021
Copyright NTT. All rights reserved.
NTT internal use only.
@author william.yizima
~~~~~~~~~~~~
Log module for viewing and troubleshoot
"""

import datetime
import logging
import logging.config
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _log_config(name: str) -> logging.Logger:
    """This function is specific for configuring logs of the scheduler type.
       This function, create in the logs/{function name} folder.
    Args:
        name ([str]): name of function

    Returns:
        [logging.Logger]: instance of Logger
    """
    datenow = datetime.datetime.now()
    datenow_format = datenow.strftime("%d-%m-%Y")
    path_log_file = os.path.join(BASE_DIR, "log", "log.ini")
    folder_log_file = os.path.join(BASE_DIR, "log/logs", name)
    is_exist = os.path.exists(folder_log_file)
    if not is_exist:
        os.makedirs(os.path.join(BASE_DIR, "log", "logs", name))

    logging.config.fileConfig(
        path_log_file,
        defaults={"logfilename": f"{folder_log_file}/{datenow_format}.log"},
    )

    logger = logging.getLogger("scheduler")
    return logger


def scheduler_log(func):
    """this function is a decorator.
    It was created to facilitate the implementation of logs.
    """

    def wrapper_repeat(*args, **kwargs):
        result = func(*args, **kwargs)
        logger = _log_config(func.__name__)
        # if needs debug
        # l_sms = f"SCHEDULER LOG - func:{func.__name__} - args:{args} - result:{result}"
        # logger.info(l_sms)
        logger.info("Function [ %s ] job has been performed", func.__name__)
        return result

    return wrapper_repeat


def error_log(message_err: str, traceback: str) -> None:
    """this function is a decorator.
    It was created to facilitate the implementation of logs.
    """
    logger = _log_config("error")
    # logger.info(f">>Error:{message_err}")
    logger.error(">>Error: %s", message_err)
    logger.error(">>>>>Traceback: %s", traceback)
