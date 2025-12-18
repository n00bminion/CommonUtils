import importlib
import pytest

# import the module that is named 'async' using importlib since 'async' is a reserved keyword
async_mod = importlib.import_module("common_utils.io_handler.external.async")


def test_async_get_raises_type_error():
    with pytest.raises(TypeError):
        async_mod.async_get()


def test_async_post_raises_type_error():
    with pytest.raises(TypeError):
        async_mod.async_post()
