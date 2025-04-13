# backend/app/services/email.py
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from backend.utils.config import settings
import logging

logger = logging.getLogger(__name__)

async def send_verification_email(email: str, username: str, token: str):
    try:
        # Construct verification URL
        verification_url = f"{settings.FRONTEND_URL}/verify-email/{token}"

        # Email content
        subject = "Verify Your Account"
        body = f"""
        Hello {username},

        Thank you for registering! Please verify your email by clicking the link below:
        {verification_url}

        This link will expire in 24 hours. If you didn’t register, please ignore this email.

        Best,
        Your App Team
        """

        # Create MIME message
        msg = MIMEMultipart()
        msg['From'] = settings.EMAIL_SENDER
        msg['To'] = email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        # Connect to SMTP server
        with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            server.sendmail(settings.EMAIL_SENDER, email, msg.as_string())

        logger.info(f"Verification email sent to {email}")
    except Exception as e:
        logger.error(f"Failed to send verification email to {email}: {str(e)}")
        raise