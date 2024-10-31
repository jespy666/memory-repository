import smtplib

from src import logger

from email.mime.text import MIMEText

from fastapi import Request

from src.config import settings


async def send_activation_email(
        request: Request,
        to_addr: str,
        token: str
) -> None:
    """
    Send email with activation link after signup.

    Args:
        request (Request): Request obj from FastAPI.
        to_addr (string): Email destination addr.
        token (string): Unique confirm token.
    """
    port = f':{request.url.port}' if request.url.port else ''
    scheme = request.url.scheme
    activation_link = (
        f"{scheme}://{request.url.hostname}{port}/activate?token={token}"
    )
    message = MIMEText(
        f'To activate your account, please follow this link:\n'
        f'{activation_link}'
    )
    message["Subject"] = "Активация аккаунта EXB"
    message["From"] = settings.SMTP_USER
    message["To"] = to_addr

    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        server.starttls()
        server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        server.sendmail(
            settings.SMTP_USER, to_addr,
            message.as_string()
        )


async def send_welcome_msg(to_addr: str) -> None:
    """
    Send welcome message to user email after success account activation.

    Args:
        to_addr (string): Addressee of the letter.
    """
    message = MIMEText(
        'Салам бро, добро пожаловать в Единое Хранилище Воспоминаний!:\n'
        'Пойми насколько тут все круто!'
    )
    message["Subject"] = "Добро пожаловать в EXB"
    message["From"] = settings.SMTP_USER
    message["To"] = to_addr

    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        server.starttls()
        server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        server.sendmail(
            settings.SMTP_USER, to_addr,
            message.as_string()
        )


async def send_activation_email_task(
        request: Request,
        email: str,
        token: str
) -> None:
    """
    Background task for activation email.
    """
    await send_activation_email(request, email, token)
    logger.info('Activation letter was send')


async def send_welcome_msg_task(to_addr: str) -> None:
    """
    Background task for welcome email.
    """
    await send_welcome_msg(to_addr)
    logger.info('Welcome letter was send')
