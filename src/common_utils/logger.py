import logging


def create_logger(logging_level=logging.CRITICAL, log_file_path="logging.log"):
    logger = logging.getLogger(__name__)
    logger.setLevel(logging_level)

    fileHandler = logging.FileHandler(log_file_path, mode="w")
    streamHandler = logging.StreamHandler()

    formatter = logging.Formatter(
        "%(levelname)s | Method: %(funcName)s | Line No.: %(lineno)d | Exec Time: %(asctime)s | Msg: %(message)s"
    )
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
