import logging
import os
import smtplib
from email.mime.text import MIMEText
from typing import Optional

logger = logging.getLogger(__name__)


class EmailClient:
    def __init__(self):
        self.provider = os.getenv("EMAIL_PROVIDER", "smtp").lower()
        self.smtp_host = os.getenv("SMTP_HOST")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_username = os.getenv("SMTP_USERNAME")
        self.smtp_password = os.getenv("SMTP_PASSWORD")
        self.smtp_from = os.getenv("SMTP_FROM", "noreply@optik-platform.com")
        self.aws_region = os.getenv("AWS_REGION", "us-east-1")

    def send_magic_link(self, to_email: str, link: str) -> bool:
        subject = "Your Optik Platform sign-in link"
        body = (
            "Use the link below to sign in. This link expires in 15 minutes.\n\n"
            f"{link}\n\n"
            "If you did not request this email, you can ignore it."
        )

        if self.provider == "ses":
            return self._send_with_ses(to_email, subject, body)

        return self._send_with_smtp(to_email, subject, body)

    def _send_with_smtp(self, to_email: str, subject: str, body: str) -> bool:
        if not all([self.smtp_host, self.smtp_username, self.smtp_password]):
            logger.warning("SMTP is not configured; skipping email send")
            return False

        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = self.smtp_from
        msg["To"] = to_email

        try:
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
            return True
        except Exception as exc:
            logger.error(f"SMTP send failed: {exc}")
            return False

    def _send_with_ses(self, to_email: str, subject: str, body: str) -> bool:
        try:
            import boto3
            client = boto3.client("ses", region_name=self.aws_region)
            client.send_email(
                Source=self.smtp_from,
                Destination={"ToAddresses": [to_email]},
                Message={
                    "Subject": {"Data": subject},
                    "Body": {"Text": {"Data": body}},
                },
            )
            return True
        except Exception as exc:
            logger.error(f"SES send failed: {exc}")
            return False
