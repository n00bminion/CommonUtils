import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os


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


def send(
    str_message: MIMEText = None,
    html_message: MIMEText = None,
    diy_message: MIMEMultipart = None,
    subject: str = None,
    recipients: list = None,
    attachment_paths: list = None,
    username: str = os.getenv("google_email_username"),
    password: str = os.getenv("google_email_password"),
):

    if not username:
        raise Exception(
            "Missing sender! Check for google_email_username in .env file or add a sender gmail email"
        )

    if not password:
        raise Exception(
            "Missing password! Check for google_email_password in .env file or add a password"
        )

    if not str_message and not html_message and not diy_message:
        raise Exception(
            "No message provided! Please provide either a text, html or diy (build your own) message to send."
        )

    msg = diy_message or MIMEMultipart()
    msg["Subject"] = subject or f"Email From {username}"
    msg["From"] = username

    if str_message:
        msg.attach(MIMEText(str_message, "plain"))

    if html_message:
        msg.attach(MIMEText(html_message, "html"))

    if attachment_paths:
        for file in attachment_paths:
            with open(file, "rb") as attachment:
                # Add file as application/octet-stream
                # Email client can usually download this automatically as attachment
                part = MIMEBase("application", "octet-stream")
                part.set_payload(attachment.read())

            # Encode file in ASCII characters to send by email
            encoders.encode_base64(part)

            # Add header as key/value pair to attachment part
            part.add_header(
                "Content-Disposition",
                f"attachment; filename= {file}",
            )

            # Add attachment to message and convert message to string
            msg.attach(part)

    _send_email(
        from_addr=username,
        to_addrs=recipients,
        password=password,
        msg=msg,
    )


def prepare_html_message(message: str):
    return f"""\
        <html>
            <head>
            </head>
            <body>
                <br>{"<br>".join(message)}<br>
            </body>
        </html>
        """


if __name__ == "__main__":
    send(
        html_message=prepare_html_message(["test"]),
        subject="testing",
        recipients=["minhtr94@hotmail.co.uk"],
    )  # this works
