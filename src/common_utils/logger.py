import logging
from common_utils import defaults
import os


@defaults.apply_defaults(
    logging_level=os.getenv("logging_level"),
    log_file_path=os.getenv("log_file_path"),
)
def create_logger(logging_level, log_file_path):
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
