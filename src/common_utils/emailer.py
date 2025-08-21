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


def build_html_email_meesage(
    style="",
    body="",
):
    return (
        "<!DOCTYPE html>"
        "<html>"
        "<head>"
        f"""
            <link rel="stylesheet" type="text/css" hs-webfonts="true" href="https://fonts.googleapis.com/css?family=Lato%7CLato:i,b,bi">
            <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
            {style}                
            </style>
        """
        "</head>"
        '<body bgcolor="#F5F8FA" style="width: 100%; font-family:Lato, sans-serif; font-size:18px; margin:0">'
        f"{body}"
        "</body>"
        "</html>",
    )


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

    if diy_message and (str_message or html_message):
        raise Exception(
            "Cannot combine diy_message with str_message or html_message. Both str_message and html_message should be None if diy_message is provided."
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
