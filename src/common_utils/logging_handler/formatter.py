import logging
from logging import Formatter

_LOGGING_FMT = "%(asctime)s - %(levelname)s - %(filename)s @ %(lineno)d [ %(funcName)s ] - %(message)s"


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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = Formatter(log_fmt)
        return formatter.format(record)


def get_custom_formatter():
    """
    Get custom formatter object.
    Returns:
        CustomFormatter object
    """
    return CustomFormatter()


def get_standard_formatter():
    """
    Get standard formatter object.
    Returns:
        Formatter object
    """
    return Formatter(_LOGGING_FMT)
