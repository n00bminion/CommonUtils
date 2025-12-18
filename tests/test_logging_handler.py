import logging
from logging import LogRecord
import sys
from common_utils.logging_handler import formatter as fmt_mod
from common_utils.logging_handler import handler as h_mod


def test_custom_formatter_formats_message():
    formatter = fmt_mod.get_custom_formatter()
    record = LogRecord("test", logging.INFO, __file__, 10, "hello %s", ("world",), None)
    out = formatter.format(record)
    assert "hello world" in out


def test_dash_output_handler_emit_appends_logs():
    dash = h_mod.DashOutputHandler(stream=sys.stdout)
    record = LogRecord("test", logging.WARNING, __file__, 20, "warned", (), None)
    dash.emit(record)
    assert any("warned" in msg for msg in dash.logs)


def test_create_stream_logging_handler_returns_handler():
    h = h_mod.create_stream_logging_handler(logging_level=logging.DEBUG)
    assert isinstance(h, logging.StreamHandler)
    # ensure formatter is an instance of logging.Formatter
    assert isinstance(h.formatter, logging.Formatter)


def test_create_dash_stream_output_logging_handler():
    h = h_mod.create_dash_stream_output_logging_handler(logging_level=logging.INFO)
    assert isinstance(h, h_mod.DashOutputHandler)
    assert isinstance(h.formatter, logging.Formatter)
