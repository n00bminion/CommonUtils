import pandas as pd
import pytest

from common_utils.data_handler import audit


def test_add_audit_columns_default():
    data = pd.DataFrame({"a": [1, 2]})
    out = audit.add_audit_columns(data.copy())

    assert "_created_date" in out.columns
    assert "_created_by" in out.columns
    assert isinstance(out["_created_date"].iloc[0], pd.Timestamp)
    assert isinstance(out["_created_by"].iloc[0], str)


def test_add_audit_columns_custom_and_type_error():
    data = pd.DataFrame({"b": [3]})
    out = audit.add_audit_columns(data.copy(), audit_columns_dict={"x": lambda: 123})
    assert "x" in out.columns
    assert out["x"].iloc[0] == 123

    with pytest.raises(ValueError):
        audit.add_audit_columns(data.copy(), audit_columns_dict="not-a-dict")


def test_remove_audit_columns_default_and_type_error():
    data = pd.DataFrame(
        {
            "a": [1],
            "_created_date": [pd.Timestamp.now()],
            "_created_by": ["host"],
        }
    )

    out = audit.remove_audit_columns(data.copy())
    assert "_created_date" not in out.columns
    assert "_created_by" not in out.columns
    assert "a" in out.columns

    # remove only specified
    data2 = pd.DataFrame(
        {
            "a": [1],
            "_created_date": [pd.Timestamp.now()],
            "_created_by": ["host"],
        }
    )
    out2 = audit.remove_audit_columns(data2.copy(), audit_columns_list=["_created_by"])
    assert "_created_by" not in out2.columns
    assert "_created_date" in out2.columns

    with pytest.raises(ValueError):
        audit.remove_audit_columns(data.copy(), audit_columns_list="not-a-list")


def test_validate_dataframe_rejects_non_df():
    with pytest.raises(ValueError):
        audit.add_audit_columns([], audit_columns_dict=None)

    with pytest.raises(ValueError):
        audit.remove_audit_columns("not-a-dataframe", audit_columns_list=None)
