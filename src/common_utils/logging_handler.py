import logging

_LOGGING_FMT = "%(asctime)s - %(levelname)s - %(filename)s @ %(lineno)d [ %(funcName)s ] - %(message)s"
_DEFAULT_LOGGER_NAME = "LOGGER"


class _CustomFormatter(logging.Formatter):
    """
    Custom class for the logging formatting. Not for direct use.
    """

    green = "\x1b[32m;20m"
    grey = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    format = _LOGGING_FMT

    FORMATS = {
        logging.DEBUG: green + format + reset,
        logging.INFO: grey + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset,
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


def create_logger(
    logger_name=_DEFAULT_LOGGER_NAME,
    logging_level=logging.DEBUG,
    handler_logging_level=None,
    log_file_path="logging.log",
):
    """
    Create logger object that can be passed around.
    It has 2 handlers, stream and file which will output the logs
    in the file passed via log_file_path argument as well as stdout.

    All the arguments have default and you can just run it like this:

    >>> logger = create_logger()

    You can also set the level to logging.INFO so it's less noisy

    >>> import logging
    >>> logger = create_logger(logging_level=logging.INFO)

    If you want to just wanna output the error to file but show all the log
    on stdout, you can use the handler_logging_level arguement. Note that
    this will only work if you leave the logging_level as logging.DEBUG.

    >>> logger = create_logger(
            handler_logging_level = {
                'file':logging.ERROR,
                'stream':logging.INFO
            }
        )

    Args:
        logger_name: name of the logger. Default is logging_handler._DEFAULT_LOGGER_NAME
        logging_level: logging level of the logger. Default is logging.DEBUG
        handler_logging_level: dict of handler name and it's logging level
        log_file_path: file path of where the logging is gonna get outputted. Default is "logging.log"

    Returns:
        logger object
    """
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging_level)

    fileHandler = logging.FileHandler(log_file_path, mode="w")
    streamHandler = logging.StreamHandler()

    fileHandler.setFormatter(logging.Formatter(_LOGGING_FMT))
    streamHandler.setFormatter(_CustomFormatter())

    allowed_handlers = {"stream": streamHandler, "file": fileHandler}

    if handler_logging_level:
        for handler_name, level in handler_logging_level:
            try:
                handler = allowed_handlers[handler_name]
            except KeyError:
                raise KeyError(
                    f"{handler_name} is not a support handler. "
                    f"The allowed handlers are {list(allowed_handlers.keys())}"
                )

            handler.setLevel(level)

    logger.addHandler(streamHandler)
    logger.addHandler(fileHandler)
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
    logger = logging.getLogger(name=logger_name)
    if not logger.handlers:
        return
    for hdlr in logger.handlers:
        hdlr.close()
        logger.removeHandler(hdlr)
