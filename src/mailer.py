import logging
import smtplib
import webbrowser
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from typing import Dict, Optional
from config import settings

logger = logging.getLogger(__name__)

def preview_in_browser(html_path: str):
    """Open the generated briefing in the system default browser."""
    abs_path = Path(html_path).resolve()
    url = abs_path.as_uri()
    logger.info(f"Opening briefing preview in browser: {url}")
    webbrowser.open(url)
    print(f"\n🌐 Briefing preview opened in your browser:\n   {url}")

def send_email(subject: str, html_content: str, text_content: str, recipient: Optional[str] = None) -> bool:
    """
    Sends the newsletter via SMTP (e.g., Gmail App Password).
    Supports multiple recipients (comma or semicolon separated).
    """
    raw_recipients = recipient or settings.RECIPIENT_EMAIL
    from_email = settings.EMAIL_FROM or settings.SMTP_USER

    if not raw_recipients or not settings.SMTP_USER or not settings.SMTP_PASSWORD:
        logger.warning("Email credentials not fully set in .env. Skipping actual SMTP dispatch.")
        print("\n" + "=" * 60)
        print("📧 [EMAIL NOTICE]")
        print(f"Recipient Email : {raw_recipients or 'Not configured'}")
        print(f"SMTP User       : {settings.SMTP_USER or 'Not configured'}")
        print("To receive daily briefings via email:")
        print("1. Set RECIPIENT_EMAIL=your_email@domain.com in your .env file")
        print("2. Set SMTP_USER=your_gmail@gmail.com and SMTP_PASSWORD=your_16_digit_app_password")
        print("=" * 60 + "\n")
        return False

    recipients = [r.strip() for r in raw_recipients.replace(";", ",").split(",") if r.strip()]

    try:
        logger.info(f"Connecting to SMTP server {settings.SMTP_HOST}:{settings.SMTP_PORT}...")
        if settings.SMTP_PORT == 465:
            server = smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT, timeout=25)
        else:
            server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=25)
            server.starttls()

        clean_user = settings.SMTP_USER.strip()
        clean_password = settings.SMTP_PASSWORD.replace(" ", "").strip()
        server.login(clean_user, clean_password)

        success_count = 0
        for rec in recipients:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = f"Tech & AI Daily <{from_email}>"
            msg["To"] = rec

            part_text = MIMEText(text_content, "plain", "utf-8")
            part_html = MIMEText(html_content, "html", "utf-8")
            msg.attach(part_text)
            msg.attach(part_html)

            try:
                server.sendmail(from_email, [rec], msg.as_string())
                logger.info(f"Briefing email successfully delivered to {rec}!")
                print(f"✅ Briefing successfully sent to {rec}")
                success_count += 1
            except Exception as send_err:
                logger.error(f"Failed to send email to {rec}: {send_err}")
                print(f"❌ Failed to send to {rec}: {send_err}")

        server.quit()
        print(f"\n🎉 Successfully sent to {success_count}/{len(recipients)} recipients!\n")
        return success_count > 0
    except Exception as e:
        logger.error(f"Failed to connect or authenticate with SMTP: {e}")
        print(f"\n❌ Error with SMTP server: {e}")
        return False
