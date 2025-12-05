import logging
from common_utils.logging_handler.handler import (
    create_file_logging_handler,
    create_stream_logging_handler,
)

_DEFAULT_LOGGER_NAME = "LOGGER"


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
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging_level)

    if not handlers:
        handlers = (
            create_stream_logging_handler(),
            create_file_logging_handler(),
        )

    if isinstance(handlers, logging.Handler):
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
    logger = logging.getLogger(name=logger_name)
    if not logger.handlers:
        return
    for hdlr in logger.handlers:
        hdlr.close()
        logger.removeHandler(hdlr)


if __name__ == "__main__":
    # logger = create_logger()
    logger = create_logger(handlers=create_stream_logging_handler())
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
