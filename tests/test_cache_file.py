from common_utils.cache_handler import file_cache


def test_prepare_cache_file_name_format():
    name = file_cache._prepare_cache_file_name(
        function_name="myfunc", datetime="20250101120000", args=(1, 2), kwargs={"a": 3}
    )
    assert name.endswith(".pkl")
    assert name.startswith("myfunc-20250101120000-")
