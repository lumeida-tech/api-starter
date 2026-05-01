import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import aiosmtplib

from core.settings import settings

logger = logging.getLogger(__name__)


async def send_email(
    *,
    to: str,
    subject: str,
    text: str,
    html: str,
) -> None:
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = f"{settings.APP_NAME} <{settings.MAIL_FROM}>"
    msg["To"]      = to
    msg.attach(MIMEText(text, "plain", "utf-8"))
    msg.attach(MIMEText(html, "html", "utf-8"))

    await aiosmtplib.send(
        msg,
        hostname=settings.MAIL_SERVER,
        port=settings.MAIL_PORT,
        username=settings.MAIL_USERNAME,
        password=settings.MAIL_PASSWORD,
        start_tls=settings.MAIL_STARTTLS,
    )
    logger.info(f"Email envoyé à {to} — {subject}")
