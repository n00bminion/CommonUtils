import logging

LOGGING_FMT = "%(levelname)s | File: %(filename)s | Line No.: %(lineno)d | Method: %(funcName)s | Exec Time: %(asctime)s | Msg: %(message)s\n"


class CustomFormatter(logging.Formatter):

    green = "\x1b[32m;20m"
    grey = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    format = LOGGING_FMT

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
    logger_name="logging",
    logging_level=logging.CRITICAL,
    log_file_path="logging.log",
):
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging_level)

    fileHandler = logging.FileHandler(log_file_path, mode="w")
    streamHandler = logging.StreamHandler()

    fileHandler.setFormatter(logging.Formatter(LOGGING_FMT))
    streamHandler.setFormatter(CustomFormatter())
    logger.addHandler(streamHandler)
    logger.addHandler(fileHandler)
    return logger


def remove_log_handlers(logger_name=__name__):
    logger = logging.getLogger(name=logger_name)
    if not logger.handlers:
        return
    for hdlr in logger.handlers:
        hdlr.close()
        logger.removeHandler(hdlr)
