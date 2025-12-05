from logging import StreamHandler, FileHandler
import logging
from common_utils.logging_handler.formatter import (
    get_custom_formatter,
    get_standard_formatter,
)
from common_utils.io_handler.file import prepare_file_path
import sys


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


def create_stream_logging_handler(logging_level=logging.NOTSET):
    """
    Create stream logging handler with custom formatter.
    Returns:
        StreamHandler object
    """
    hdlr = StreamHandler()
    hdlr.setFormatter(get_custom_formatter())
    hdlr.setLevel(logging_level)
    return hdlr


def create_file_logging_handler(
    log_file_path="logging.log", logging_level=logging.NOTSET
):
    """
    Create file logging handler with standard formatter.
    Args:
        log_file_path: path to the log file. Default is 'logging.log'
    Returns:
        FileHandler object
    """
    prepare_file_path(log_file_path)
    hdlr = FileHandler(log_file_path, mode="w")
    hdlr.setFormatter(get_standard_formatter())
    hdlr.setLevel(logging_level)
    return hdlr


def create_dash_stream_output_logging_handler(logging_level=logging.NOTSET):
    """
    Create Dash stream logging handler with standard formatter.
    Returns:
        DashOutputHandler object
    """
    hdlr = DashOutputHandler(stream=sys.stdout)
    hdlr.setFormatter(get_standard_formatter())
    hdlr.setLevel(logging_level)
    return hdlr
