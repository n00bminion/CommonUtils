from common_utils import process_handler
import time


def _io_test_function(sleep_time: int, return_value: str):
    print(f"Sleeping for {sleep_time} seconds...")
    time.sleep(sleep_time)
    print(f"Returning value = {return_value}")
    return return_value


def test_use_multi_thread():
    args = [(1, "first"), (5, "second"), (3, "third"), (3, "fourth")]
    results = process_handler.use_multi_thread(_io_test_function, args)

    assert results == {
        (1, "first"): "first",
        (3, "third"): "third",
        (3, "fourth"): "fourth",
        (5, "second"): "second",
    }
