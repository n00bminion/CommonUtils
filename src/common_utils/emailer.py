import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os


def _send_email(from_addr, to_addrs, password, msg, host="smtp.gmail.com", port=587):
    """
    Hidden function with basic email sending capability.

    Args:
        from_addr: email address to send email from,
        to_addrs: list of email addresses to send email to,
        password: password to log into email account,
        msg: html message,
        host: email host. Defaults to "smtp.gmail.com",
        port: email port. Defaults to 587

    Return:
        None
    """
    try:
        with smtplib.SMTP(
            host=host,
            port=port,
        ) as server:
            server.starttls()
            server.ehlo()
            server.login(
                user=msg["From"],
                password=password,
            )
            server.sendmail(
                from_addr=from_addr,
                to_addrs=to_addrs,
                msg=msg.as_string(),
            )
            server.quit()

    except Exception as e:
        raise e


def build_html_email_meesage(
    style="",
    body="",
):
    """
    Premade HTML canvas that where we can fill in the style and body content with HTML string

    Args:
        style: style html
        body: body html

    Return:
        None
    """
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
        "</html>"
    )


def send(
    str_message: str = None,
    html_message: str = None,
    diy_message: MIMEMultipart = None,
    subject: str = None,
    recipients: list = None,
    attachment_paths: list = None,
    username: str = os.getenv("google_email_username"),
    password: str = os.getenv("google_email_password"),
):
    """
    Function to send email.

    Args:
        str_message: simple str content to put into email
        html_message: simple html content to put into email
        diy_message: html content to put into email (use build_html_email_meesage function to help build and format email)
        subject: email subject
        recipients: list of email recipients
        attachment_paths: list = list of attachments file path that can be added attachment to email
        username: email username
        password: email password

    Return:
        None
    """

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

    if diy_message:
        if not isinstance(diy_message, MIMEMultipart):
            raise ValueError(
                f"diy_message must be of type MIMEMultipart but got {type(diy_message)}"
            )
        msg = diy_message
    else:
        msg = MIMEMultipart()
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
