import logging
import smtplib
from email.message import EmailMessage

from backend.config import settings

logger = logging.getLogger(__name__)

async def send_verification_email(to_email: str, token: str) -> None:
    """Send an email verification link to the user."""
    if not settings.smtp_host:
        logger.warning(f"SMTP is disabled. Verification link for {to_email}: {settings.frontend_url}/verify-email?token={token}")
        return

    verify_link = f"{settings.frontend_url}/verify-email?token={token}"
    
    msg = EmailMessage()
    msg["Subject"] = "Verify your CodeArena account"
    msg["From"] = settings.smtp_from_email
    msg["To"] = to_email
    
    # Simple plain text email (can be upgraded to HTML later)
    msg.set_content(
        f"Welcome to CodeArena!\n\n"
        f"Please verify your email address by clicking the link below:\n\n"
        f"{verify_link}\n\n"
        f"This link will expire in 30 minutes.\n\n"
        f"If you did not create an account, you can safely ignore this email."
    )

    try:
        # Run synchronous SMTP code in a way that doesn't block the async loop
        # For a simple setup, we'll use a local import of asyncio to run_in_executor
        import asyncio
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, _send_email_sync, msg)
        logger.info(f"Verification email sent to {to_email}")
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {e}")

def _send_email_sync(msg: EmailMessage) -> None:
    """Synchronous function to actually send the email via smtplib."""
    with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
        if settings.smtp_port == 587:
            server.starttls()
        if settings.smtp_user and settings.smtp_password:
            server.login(settings.smtp_user, settings.smtp_password)
        server.send_message(msg)
