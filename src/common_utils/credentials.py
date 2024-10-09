import functools
from dotenv import load_dotenv
import os

load_dotenv()


def apply_default_sender_detail(function):
    return functools.partial(
        function,
        sender=os.getenv("google_email_app_username"),
        password=os.getenv("google_email_app_password"),
    )
