import logging
from typing import Any, Dict, List, Optional
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)


def send_app_email(subject: str,
                   recipient_list: List[str],
                   template_name: str,
                   context: Optional[Dict[str, Any]] = None,
                   from_email: Optional[str] = None,
                   fail_silently: bool = False) -> bool:
    """
    Reusable email dispatch service supporting plain text & HTML templates.

    :param subject: Email subject line.
    :param recipient_list: List of recipient email addresses.
    :param template_name: Relative path to template without extension (e.g. 'emails/contact_inquiry').
    :param context: Dictionary context passed to the template renderer.
    :param from_email: Sender address (defaults to settings.DEFAULT_FROM_EMAIL).
    :param fail_silently: If True, suppresses exceptions and returns False on failure.
    :return: True if email dispatched successfully, False otherwise.
    """
    if context is None:
        context = {}

    sender: str = from_email or getattr(settings, "DEFAULT_FROM_EMAIL",
                                        "webmaster@localhost")

    try:
        text_content: str = render_to_string(f"{template_name}.txt", context)
        html_content: str = render_to_string(f"{template_name}.html", context)

        email = EmailMultiAlternatives(subject=subject,
                                       body=text_content,
                                       from_email=sender,
                                       to=recipient_list)
        email.attach_alternative(html_content, "text/html")
        email.send(fail_silently=fail_silently)

        logger.info(f"Email '{subject}' successfully sent to {recipient_list}")
        return True

    except Exception as e:
        logger.error(
            f"Failed to send email '{subject}' to {recipient_list}: {str(e)}",
            exc_info=True)
        if not fail_silently:
            raise e
        return False
