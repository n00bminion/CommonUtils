from datetime import datetime, timezone
from functools import singledispatch
import pandas as pd


@singledispatch
def derive_date_object(datetime_obj, tz):
    """
    Derive date from a datetime or string object and applies timezone (if passed in)
    The string object needs to be of iso format

    Args:
        datetime_obj: string or datetime object
        tz: timezone object (check timezone module for more info), defaults to timezone.utc
    Return:
        datetime object

    """

    raise ValueError(
        f"Invalid datetime_obj parameter. Must be None, a datetime object, or an ISO format string but was passed {type(datetime_obj)}"
    )


@derive_date_object.register(str)
def _str(datetime_obj, tz):
    try:
        dt = datetime.fromisoformat(datetime_obj)
        return dt.astimezone(tz)
    except ValueError:
        pass


@derive_date_object.register(datetime)
def _dt(datetime_obj, tz):
    return datetime_obj.astimezone(tz)


@derive_date_object.register(type(None))
def _none(datetime_obj, tz):
    return datetime.now(tz=tz)


def get_timestamp(datetime_obj=None, tz=timezone.utc):
    return derive_date_object(datetime_obj, tz=tz)


def get_unix_timestamp(datetime_obj=None, tz=timezone.utc):
    return get_timestamp(datetime_obj, tz).timestamp()


def get_str_timestamp(datetime_obj=None, tz=timezone.utc):
    return get_timestamp(datetime_obj, tz).isoformat(" ")


def get_str_datestamp(datetime_obj=None, tz=timezone.utc):
    return get_timestamp(datetime_obj, tz).date().isoformat()


def get_pandas_timestamp(datetime_obj=None, tz=None):
    # remove time zone to make column smaller
    return pd.Timestamp(get_timestamp(datetime_obj, tz))


if __name__ == "__main__":
    print(get_pandas_timestamp("2023-11-12 15:00:02"))
