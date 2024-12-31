import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os


def send(
    username: str = os.getenv("google_email_app_username"),
    password: str = os.getenv("google_email_app_password"),
    recipients_list: list = None,
    subject: str = None,
    message: str = None,
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

    with smtplib.SMTP(host="smtp.gmail.com", port=587) as server:
        server.starttls()
        server.ehlo()
        server.login(
            user=msg["From"],
            password=password,
        )
        server.sendmail(
            from_addr=username, to_addrs=recipients_list, msg=msg.as_string()
        )
        server.quit()


if __name__ == "__main__":
    send(
        recipients_list=["minhtr94@gmail.com"],
        subject="testing",
        message="test",
    )
