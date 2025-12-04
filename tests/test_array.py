from common_utils.data_handler import array


def test_chunk_iter():
    data = [1, 2, 3, 4, 5]
    chunks = list(array.chunk_iter(data, 2))
    assert chunks == [[1, 2], [3, 4], [5]]
