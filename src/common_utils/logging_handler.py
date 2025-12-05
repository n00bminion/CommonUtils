import logging
from logging import (
    Formatter,
    StreamHandler,
    FileHandler,
    Handler,
    getLogger,
)
import sys
from common_utils.io_handler.file import prepare_file_path

_LOGGING_FMT = "%(asctime)s - %(levelname)s - %(filename)s @ %(lineno)d [ %(funcName)s ] - %(message)s"
_DEFAULT_LOGGER_NAME = "LOGGER"


class DashOutputHandler(StreamHandler):
    """
    Logger class to capture logs for Dash applications. Link for this and usage:
    https://www.pueschel.dev/python,/dash,/plotly/2019/06/28/dash-logs.html
    """

    def __init__(self, stream=None):
        super().__init__(stream=stream)
        self.logs = list()

    def emit(self, record):
        try:
            msg = self.format(record)
            self.logs.append(msg)
            self.logs = self.logs[-1000:]
            self.flush()
        except Exception:
            self.handleError(record)


class CustomFormatter(Formatter):
    """
    Custom class for the logging formatting based on the level of the log message.
    """

    # ANSI Color Codes - https://talyian.github.io/ansicolors/
    green = "\x1b[32m;20m"
    grey = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"

    reset = "\x1b[0m"
    format = _LOGGING_FMT

    FORMATS = {
        logging.NOTSET: grey + format + reset,
        logging.DEBUG: green + format + reset,
        logging.INFO: grey + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset,
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = Formatter(log_fmt)
        return formatter.format(record)


def create_stream_logging_handler():
    """
    Create stream logging handler with custom formatter.
    Returns:
        StreamHandler object
    """
    hdlr = StreamHandler()
    hdlr.setFormatter(CustomFormatter())
    return hdlr


def create_file_logging_handler(log_file_path="logging.log"):
    """
    Create file logging handler with standard formatter.
    Args:
        log_file_path: path to the log file. Default is 'logging.log'
    Returns:
        FileHandler object
    """
    prepare_file_path(log_file_path)
    hdlr = FileHandler(log_file_path, mode="w")
    hdlr.setFormatter(Formatter(_LOGGING_FMT))
    return hdlr


def create_dash_stream_output_logging_handler():
    """
    Create Dash stream logging handler with standard formatter.
    Returns:
        DashOutputHandler object
    """
    hdlr = DashOutputHandler(stream=sys.stdout)
    hdlr.setFormatter(Formatter(_LOGGING_FMT))
    return hdlr


def create_logger(
    logger_name=_DEFAULT_LOGGER_NAME,
    logging_level=logging.DEBUG,
    handlers=None,
):
    """
    Create logger object that can be passed around with 2 handlers by default: stream and file handlers.

    All the arguments have default and you can just run it like this:

    >>> logger = create_logger()

    You can also set the level to logging.INFO so it's less noisy

    >>> import logging
    >>> logger = create_logger(logging_level=logging.INFO)

    Args:
        logger_name: name of the logger. Default is logging_handler._DEFAULT_LOGGER_NAME
        logging_level: logging level of the logger. Default is logging.DEBUG
        handlers: list or tuple of logging handlers or a single handler. Default is None, which creates stream and file handlers (see create_file_logging_handler and create_stream_logging_handler)

    Returns:
        logger object
    """
    logger = getLogger(logger_name)
    logger.setLevel(logging_level)

    if not handlers:
        handlers = (
            create_stream_logging_handler(),
            create_file_logging_handler(),
        )

    if isinstance(handlers, Handler):
        handlers = [handlers]

    for handler in handlers:
        logger.addHandler(handler)

    return logger


def remove_log_handlers(logger_name=_DEFAULT_LOGGER_NAME):
    """
    Simple function to remove all the handlers from a logger.
    Won't need most of the time unless cleaning of the logger is need
    at the end, maybe in context manager?

    Args:
        logger_name: name of the logger. Default is logging_handler._DEFAULT_LOGGER_NAME

    Returns:
        None
    """
    logger = getLogger(name=logger_name)
    if not logger.handlers:
        return
    for hdlr in logger.handlers:
        hdlr.close()
        logger.removeHandler(hdlr)
