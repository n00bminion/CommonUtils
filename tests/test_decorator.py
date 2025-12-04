import pandas as pd
from common_utils.data_handler import decorator


def test_add_created_audit_columns_default():
    @decorator.add_created_audit_columns
    def make_df():
        return pd.DataFrame({"a": [1, 2]})

    df = make_df()
    assert "_created_date" in df.columns
    assert "_created_by" in df.columns
    assert all(col in df.columns for col in ["a", "_created_date", "_created_by"])


def test_add_created_audit_columns_options():
    @decorator.add_created_audit_columns(add_created_by=False)
    def make_df2():
        return pd.DataFrame({"b": [3]})

    df2 = make_df2()
    assert "_created_date" in df2.columns
    assert "_created_by" not in df2.columns
