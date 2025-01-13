import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
from functools import singledispatch


def _send_email(from_addr, to_addrs, password, msg):
    try:
        with smtplib.SMTP(host="smtp.gmail.com", port=587) as server:
            server.starttls()
            server.ehlo()
            server.login(
                user=msg["From"],
                password=password,
            )
            server.sendmail(from_addr=from_addr, to_addrs=to_addrs, msg=msg.as_string())
            server.quit()

    except Exception as e:
        raise e


@singledispatch
def send(
    message,
    subject=None,
    recipients=None,
    username=os.getenv("google_email_app_username"),
    password=os.getenv("google_email_app_password"),
):
    raise NotImplementedError("Unsupported message type")


@send.register
def _send_simple_string_message(
    message: str,
    subject: str = None,
    recipients: list = None,
    username: str = os.getenv("google_email_app_username"),
    password: str = os.getenv("google_email_app_password"),
):
    if not username:
        raise Exception(
            "Missing sender! Check for google_email_app_username in .env file or add a sender gmail email"
        )

    if not password:
        raise Exception(
            "Missing password! Check for google_email_app_password in .env file or add a password"
        )

    msg = MIMEMultipart()
    msg["Subject"] = subject
    msg["From"] = username

    msg.attach(
        MIMEText(
            f"""\
        <html>
            <head>
            </head>
            <body>
                <br>{"<br>".join(message)}<br>
            </body>
        </html>
        """,
            "html",
        )
    )

    _send_email(
        from_addr=username,
        to_addrs=recipients,
        password=password,
        msg=msg,
    )


@send.register
def _send_mimemultipart_message(
    message: MIMEMultipart,
    subject: str = None,
    recipients: list = None,
    username: str = os.getenv("google_email_app_username"),
    password: str = os.getenv("google_email_app_password"),
):
    if not username:
        raise Exception(
            "Missing sender! Check for google_email_app_username in .env file or add a sender gmail email"
        )

    if not password:
        raise Exception(
            "Missing password! Check for google_email_app_password in .env file or add a password"
        )

    msg = message
    msg["Subject"] = subject
    msg["From"] = username

    _send_email(
        from_addr=username,
        to_addrs=recipients,
        password=password,
        msg=msg,
    )


if __name__ == "__main__":
    send("test", subject="testing", recipients=["minhtr94@gmail.com"])  # this works
