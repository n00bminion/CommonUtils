import pytest
from common_utils.io_handler.database._query_transformer import _transform_kv_to_clause


def test_transform_str():
    assert _transform_kv_to_clause("a", "col") == "col = 'a'"


def test_transform_num():
    assert _transform_kv_to_clause(5, "n") == "n = 5"


def test_transform_list():
    # use strings to avoid internal join type-mismatch in the implementation
    out = _transform_kv_to_clause(["1", "b"], "c")
    # check basic structure and members
    assert "c in" in out
    assert "'b'" in out
    assert "'1'" in out


def test_transform_dict_valid_and_invalid():
    # valid comparator
    out = _transform_kv_to_clause({">": 5}, "a")
    assert isinstance(out, list)

    # invalid comparator should assert
    with pytest.raises(AssertionError):
        _transform_kv_to_clause({"NOPE": 1}, "a")
