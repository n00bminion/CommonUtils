import os
import datetime
from common_utils.io_handler import file
import glob
import common_utils

CACHE_FOLDER = f".{common_utils.__package__}_cache"
COMMON_SEPARATOR = "-"
DATETIME_FORMAT = "%Y%m%d%H%M%S"
SECONDS_IN_DAY = 86400


def _prepare_cache_file_name(
    function_name: str,
    datetime: str,
    args: tuple,
    kwargs: dict,
) -> str:
    # convert list to tuple to do the hashing
    # tuple of arguments
    if args:
        args = (tuple(arg) if isinstance(arg, list) else arg for arg in args)
        print(
            f"non keyword argument(s) of type 'list' is temporarily converted to 'tuple' for function '{function_name}' "
            "to allow for hashing of arguments to derive cache file name"
        )

    # dict of keyword arguments
    if kwargs:
        kwargs = {k: tuple(v) if isinstance(v, list) else v for k, v in kwargs.items()}
        print(
            f"keyword argument(s) of type 'list' is temporarily converted to 'tuple' for function '{function_name}' "
            "to allow for hashing of keyword arguments to derive cache file name"
        )

    return (
        COMMON_SEPARATOR.join(
            (
                function_name,
                datetime,
                str(hash(args)),
                str(hash(tuple(kwargs.items()))),
            )
        )
        + ".pkl"
    )


def _prepare_latest_cache_file_name(cache_file_path_pattern):
    return file.prepare_file_path(
        f"{CACHE_FOLDER}/{cache_file_path_pattern.replace('*', datetime.datetime.now().strftime(DATETIME_FORMAT))}"
    )


def _remove_old_cache(old_cache_file_path, days_to_keep, *f_args, **f_kwargs):
    assert isinstance(days_to_keep, (int, float)), (
        f"days_to_keep must be a numeric type (int or float). Got {type(days_to_keep)} instead."
    )

    # no file to we can skip deletion OR negative value implies never remove
    if not old_cache_file_path:
        return

    (
        _,
        old_created_datetime_str,
        _,
        _,
    ) = old_cache_file_path.split(COMMON_SEPARATOR)

    old_created_datetime = datetime.datetime.strptime(
        old_created_datetime_str, DATETIME_FORMAT
    )

    # check if old file is older than days_to_keep, 2 d.p is allowed for comparison
    day_difference = round(
        (datetime.datetime.now() - old_created_datetime).total_seconds()
        / SECONDS_IN_DAY,
        2,
    )

    if day_difference >= days_to_keep:
        file.remove_file(file_path=old_cache_file_path)
        return
    elif day_difference < days_to_keep:
        return

    raise ValueError("Unable to remove cache files. Check the implementation...")


def cache_to_file(*args, days_to_keep=1):
    """
    Decorator to cache function output to a file.

    Args:
        days_to_keep (int/float): Number of days to keep the cache file. Must be > 0.
        days_to_keep can also be a float to allowed for 0.5 days or 0.25 days. Maximum 2 d.p is allowed.
    Returns:
        function output or cached file content

    """

    def write_and_or_open_cache(function):
        def wrapper(*f_args, **f_kwargs):
            if days_to_keep <= 0:
                raise ValueError(
                    f"Number of days to keep the file cannot be less than or equal to 0... {days_to_keep} days was passed in"
                )

            cache_file_path_pattern = _prepare_cache_file_name(
                function_name=function.__name__,
                datetime="*",
                args=f_args,
                kwargs=f_kwargs,
            )

            old_cache_file_paths = glob.glob(
                pathname=f"{CACHE_FOLDER}/{cache_file_path_pattern}"
            )

            latest_cache_file_path = _prepare_latest_cache_file_name(
                cache_file_path_pattern
            )

            # if no old cache file then we run the code and save the file
            if len(old_cache_file_paths) == 0:
                file.save_to_file(
                    content := function(*f_args, **f_kwargs),
                    file_path=latest_cache_file_path,
                    open_mode="wb",
                    build_parent_dir=False,  # already built in _prepare_cache_file_path
                )
                return content

            # raise error if more than 1 file
            elif len(old_cache_file_paths) > 1:
                raise ValueError(
                    f"More than one cache file found for function {function.__name__} with args {f_args} and kwargs {f_kwargs}. Files: {old_cache_file_paths}"
                )

            else:
                # if 1 file then we proceed
                old_cache_file_path = old_cache_file_paths[0]

                _remove_old_cache(
                    old_cache_file_path=old_cache_file_path,
                    days_to_keep=days_to_keep,
                    *f_args,
                    **f_kwargs,
                )

                # _remove_old_caches might either remove old cache file or not done anything
                # if old file isn't deleted, we return it
                if os.path.isfile(old_cache_file_path):
                    return file.read_file(
                        file_path=old_cache_file_path, open_mode="rb"
                    )  # this might not work

                # otherwise we save the data to file first and then return data
                file.save_to_file(
                    content := function(*f_args, **f_kwargs),
                    file_path=latest_cache_file_path,
                    open_mode="wb",
                    build_parent_dir=False,  # already built in _prepare_cache_file_path
                )
                return content

        return wrapper

    # take default argument days_to_keep
    if len(args) > 0:
        if callable(args[0]):
            return write_and_or_open_cache(args[0])

    return write_and_or_open_cache
