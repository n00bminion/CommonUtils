import requests


def get_request(*args, **kwargs):
    """
    Wrapper around requests.get function that
    deals with status code and returns the response object

    Args:
        *args: positional args to use in requests.get
        **kwargs: keyword args to use in requests.get

    Returns:
        Response object

    """
    response = requests.get(*args, **kwargs)
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        raise e

    return response


def post_request(*args, **kwargs):
    """
    Wrapper around requests.post function that
    deals with status code and returns the response object

    Args:
        *args: positional args to use in requests.post
        **kwargs: keyword args to use in requests.post

    Returns:
        Response object

    """
    response = requests.post(*args, **kwargs)
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        raise e

    return response
