import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from common_utils import defaults
import os


@defaults.apply_defaults(
    sender=os.getenv("google_email_app_username"),
    password=os.getenv("google_email_app_password"),
)
def send(sender: str, password: str, recipients_list: list, subject: str, message: str):
    """ """
    if not sender:
        raise Exception(
            "Missing sender! Check for google_email_app_username in .env file or add a sender gmail email"
        )

    if not password:
        raise Exception(
            "Missing password! Check for google_email_app_password in .env file or add a password"
        )

    msg = MIMEMultipart()
    msg["Subject"] = subject
    msg["From"] = sender

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
        server.sendmail(from_addr=sender, to_addrs=recipients_list, msg=msg.as_string())
        server.quit()
