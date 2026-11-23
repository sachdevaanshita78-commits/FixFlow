
import os
import smtplib
import ssl

from dotenv import load_dotenv
from email.message import EmailMessage

load_dotenv()


def send_email(
    recipient: str,
    subject: str,
    body: str,
) -> None:
    """Send a plain-text email through Gmail SMTP."""

    smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    sender_email = os.getenv("SMTP_EMAIL")
    app_password = os.getenv("SMTP_APP_PASSWORD")

    if not sender_email or not app_password:
        raise RuntimeError("SMTP credentials are missing from .env")

    message = EmailMessage()
    message["From"] = sender_email
    message["To"] = recipient
    message["Subject"] = subject
    message.set_content(body)

    context = ssl.create_default_context()

    with smtplib.SMTP(smtp_host, smtp_port, timeout=20) as server:
        server.ehlo()
        server.starttls(context=context)
        server.ehlo()
        server.login(sender_email, app_password)
        server.send_message(message)


def send_invitation_email(
    recipient_email: str,
    recipient_name: str,
    company_name: str,
    invitation_token: str,
) -> None:
    """Send an invitation to join a company on FixFlow."""

    invitation_url = (
        "http://localhost:5173/accept-invitation"
        f"?token={invitation_token}"
    )

    subject = f"Invitation to join {company_name} on FixFlow"

    body = f"""
Hello {recipient_name},

You have been invited to join {company_name} on FixFlow.

To accept your invitation, open the link below:

{invitation_url}

This invitation expires in 24 hours.

If you were not expecting this invitation, you can ignore this email.

Regards,
FixFlow Team
"""

    send_email(
        recipient=recipient_email,
        subject=subject,
        body=body,
    )
