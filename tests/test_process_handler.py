from common_utils import process_handler


# top-level function so it is picklable for multiprocessing on Windows
def multiply(x):
    return x * x


def test_use_multi_thread():
    res = process_handler.use_multi_thread(multiply, [1, 2, 3])
    assert res == [1, 4, 9]


def test_use_multi_process():
    # multiprocessing can be flaky on some CI; exercise a simple top-level function
    res = process_handler.use_multi_process(multiply, [2, 3, 4])
    assert sorted(res) == sorted([4, 9, 16])
