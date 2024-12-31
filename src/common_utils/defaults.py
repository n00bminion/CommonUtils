from functools import wraps, partial
from dotenv import load_dotenv

load_dotenv()


def apply_defaults(*args, **kwargs):
    def decorator(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            return partial(function, *args, **kwargs)

        return wrapper

    return decorator


# def apply_default_sender_detail(function):
#     return partial(
#         function,
#         sender=os.getenv("google_email_app_username"),
#         password=os.getenv("google_email_app_password"),
#     )
