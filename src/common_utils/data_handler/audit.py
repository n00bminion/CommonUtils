import pandas as pd
import socket
from common_utils.datetime_handler import get_pandas_timestamp

DEFAULT_AUDIT_COLUMNS = {
    "_created_date": get_pandas_timestamp,
    "_created_by": socket.gethostname,
}


def _validate_dataframe(data):
    if type(data) is not pd.DataFrame:
        raise ValueError(f"data must be of type pandas DataFrame but got {type(data)}")


def add_audit_columns(data, audit_columns_dict=None):
    """
    Add audit columns to a dataframe.
    By default, it will columns which are set in the global variable DEFAULT_AUDIT_COLUMNS but a custom
    dictionary can be passed in via the audit_columns_dict parameter.

    Args:
        data: pandas DataFrame to add audit columns to
        audit_columns_dict: dictionary of column names and functions to generate their values
    Return:
        pandas DataFrame
    """
    _validate_dataframe(data)

    if audit_columns_dict is None:
        audit_columns_dict = DEFAULT_AUDIT_COLUMNS

    if not isinstance(audit_columns_dict, dict):
        raise ValueError(
            "audit_columns_dict must be of type dict "
            f"but got {type(audit_columns_dict)}"
        )

    return data.assign(
        **{
            col_name: col_function()
            for col_name, col_function in audit_columns_dict.items()
        }
    )


def remove_audit_columns(data, audit_columns_list=None):
    """
    Remove audit columns from a dataframe.
    By default, it will remove columns which are set in the global variable AUDIT_COLUMNS but a custom
    list can be passed in via the audit_columns_list parameter.
    Args:
        data: pandas DataFrame with audit columns
        audit_columns_list: list, set or tuple of column names to remove

    Return:
        pandas DataFrame

    """

    _validate_dataframe(data)

    if audit_columns_list is None:
        audit_columns_list = set(DEFAULT_AUDIT_COLUMNS.keys())

    if not isinstance(audit_columns_list, (list, set, tuple)):
        raise ValueError(
            "audit_columns_list must be of type list, set, or tuple "
            f"but got {type(audit_columns_list)}"
        )

    existing_columns = list(set(audit_columns_list).intersection(set(data.columns)))

    if not existing_columns:
        raise ValueError("Cannot drop audit columns, no audit columns were found...")

    return data.drop(columns=existing_columns)


if __name__ == "__main__":
    data = pd.DataFrame({"a": [1, 2, 3]})

    data_with_audit = add_audit_columns(data)
    print("With audit columns:")
    print(data_with_audit)
    data_without_audit = remove_audit_columns(data_with_audit)
    print("Without audit columns:")
    print(data_without_audit)
