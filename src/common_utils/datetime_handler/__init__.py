from datetime import datetime, timezone

raise NotImplementedError("This module is not in use, do not import.")


def derive_date_from_parameter(datetime_obj, tz):
    if datetime_obj is None:
        return datetime.now(tz=tz)

    if isinstance(datetime_obj, datetime):
        return datetime_obj.astimezone(tz)

    if isinstance(datetime_obj, str):
        try:
            dt = datetime.fromisoformat(datetime_obj)
            return dt.astimezone(tz)
        except ValueError:
            pass

    raise ValueError(
        "Invalid datetime_obj parameter. Must be None, a datetime object, or an ISO format string."
    )


def get_timestamp(datetime_obj=None, tz=timezone.utc):
    return derive_date_from_parameter(datetime_obj, tz=tz).isoformat(" ")


def get_year(datetime_obj=None, tz=timezone.utc):
    return derive_date_from_parameter(datetime_obj, tz=tz).year


def get_month(datetime_obj=None, tz=timezone.utc):
    return derive_date_from_parameter(datetime_obj, tz=tz).month


def get_day(datetime_obj=None, tz=timezone.utc):
    return derive_date_from_parameter(datetime_obj, tz=tz).day
