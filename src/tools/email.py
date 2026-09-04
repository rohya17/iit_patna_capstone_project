"""
Email sending utility module.

Provides functionality to send emails via SMTP.
"""
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from src.config import config
from src.logger import logger


def send_email(subject: str, body: str, email_address: str) -> bool:
    """
    Send an email via SMTP.

    Args:
        subject: The email subject line
        body: The email body content (plain text)
        email_address: The recipient email address

    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    # Check if email is enabled in config
    if not config.EMAIL.get("enabled", False):
        logger.warning("Email sending is disabled in configuration")
        return False

    # Validate required configuration
    smtp_host = config.EMAIL.get("smtp_host")
    smtp_port = config.EMAIL.get("smtp_port")
    use_tls = config.EMAIL.get("use_tls", True)
    from_email = config.EMAIL.get("from_email")
    from_name = config.EMAIL.get("from_name", "Service Team")
    smtp_username = config.SMTP_USERNAME
    smtp_password = config.SMTP_PASSWORD

    if not all([smtp_host, smtp_port, from_email, smtp_username, smtp_password]):
        logger.error("Email configuration incomplete. Check config.toml and .env")
        return False

    try:
        # Create message
        msg = MIMEMultipart()
        msg["From"] = f"{from_name} <{from_email}>"
        msg["To"] = email_address
        msg["Subject"] = subject

        # Attach body as plain text
        msg.attach(MIMEText(body, "plain", "utf-8"))

        # Create secure SSL context
        context = ssl.create_default_context()

        # Connect to SMTP server
        if use_tls:
            # Use STARTTLS (port 587 typically)
            with smtplib.SMTP(smtp_host, smtp_port, timeout=30) as server:
                server.ehlo()
                server.starttls(context=context)
                server.ehlo()
                server.login(smtp_username, smtp_password)
                server.send_message(msg)
        else:
            # Use SSL/TLS directly (port 465 typically)
            with smtplib.SMTP_SSL(smtp_host, smtp_port, context=context, timeout=30) as server:
                server.login(smtp_username, smtp_password)
                server.send_message(msg)

        logger.info(f"Email sent successfully to {email_address}")
        return True

    except smtplib.SMTPAuthenticationError as e:
        logger.error(f"SMTP authentication failed: {e}")
        return False
    except smtplib.SMTPRecipientsRefused as e:
        logger.error(f"Recipient refused: {e}")
        return False
    except smtplib.SMTPSenderRefused as e:
        logger.error(f"Sender refused: {e}")
        return False
    except smtplib.SMTPDataError as e:
        logger.error(f"SMTP data error: {e}")
        return False
    except smtplib.SMTPException as e:
        logger.error(f"SMTP error occurred: {e}")
        return False
    except ConnectionError as e:
        logger.error(f"Connection error: {e}")
        return False
    except TimeoutError as e:
        logger.error(f"Connection timeout: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error sending email: {e}")
        return False


def send_html_email(subject: str, html_body: str, email_address: str, text_body: str) -> bool:
    """
    Send an HTML email via SMTP with optional plain text fallback.

    Args:
        subject: The email subject line
        html_body: The email body content (HTML)
        email_address: The recipient email address
        text_body: Optional plain text fallback body

    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    # Check if email is enabled in config
    if not config.EMAIL.get("enabled", False):
        logger.warning("Email sending is disabled in configuration")
        return False

    # Validate required configuration
    smtp_host = config.EMAIL.get("smtp_host")
    smtp_port = config.EMAIL.get("smtp_port")
    use_tls = config.EMAIL.get("use_tls", True)
    from_email = config.EMAIL.get("from_email")
    from_name = config.EMAIL.get("from_name", "Service Team")
    smtp_username = config.SMTP_USERNAME
    smtp_password = config.SMTP_PASSWORD

    if not all([smtp_host, smtp_port, from_email, smtp_username, smtp_password]):
        logger.error("Email configuration incomplete. Check config.toml and .env")
        return False

    try:
        # Create message
        msg = MIMEMultipart("alternative")
        msg["From"] = f"{from_name} <{from_email}>"
        msg["To"] = email_address
        msg["Subject"] = subject

        # Attach plain text version if provided
        if text_body:
            msg.attach(MIMEText(text_body, "plain", "utf-8"))

        # Attach HTML version
        msg.attach(MIMEText(html_body, "html", "utf-8"))

        # Create secure SSL context
        context = ssl.create_default_context()

        # Connect to SMTP server
        if use_tls:
            # Use STARTTLS (port 587 typically)
            with smtplib.SMTP(smtp_host, smtp_port, timeout=30) as server:
                server.ehlo()
                server.starttls(context=context)
                server.ehlo()
                server.login(smtp_username, smtp_password)
                server.send_message(msg)
        else:
            # Use SSL/TLS directly (port 465 typically)
            with smtplib.SMTP_SSL(smtp_host, smtp_port, context=context, timeout=30) as server:
                server.login(smtp_username, smtp_password)
                server.send_message(msg)

        logger.info(f"HTML email sent successfully to {email_address}")
        return True

    except smtplib.SMTPAuthenticationError as e:
        logger.error(f"SMTP authentication failed: {e}")
        return False
    except smtplib.SMTPRecipientsRefused as e:
        logger.error(f"Recipient refused: {e}")
        return False
    except smtplib.SMTPSenderRefused as e:
        logger.error(f"Sender refused: {e}")
        return False
    except smtplib.SMTPDataError as e:
        logger.error(f"SMTP data error: {e}")
        return False
    except smtplib.SMTPException as e:
        logger.error(f"SMTP error occurred: {e}")
        return False
    except ConnectionError as e:
        logger.error(f"Connection error: {e}")
        return False
    except TimeoutError as e:
        logger.error(f"Connection timeout: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error sending email: {e}")
        return False