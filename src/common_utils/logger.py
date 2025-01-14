import logging

LOGGING_FMT = "%(levelname)s | File: %(pathname)s | Line No.: %(lineno)d | Method: %(funcName)s | Exec Time: %(asctime)s | Msg: %(message)s"


def create_logger(
    logger_name="logging",
    logging_level=logging.CRITICAL,
    log_file_path="logging.log",
):
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging_level)

    fileHandler = logging.FileHandler(log_file_path, mode="w")
    streamHandler = logging.StreamHandler()

    formatter = logging.Formatter(LOGGING_FMT)
    fileHandler.setFormatter(formatter)
    streamHandler.setFormatter(formatter)
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
