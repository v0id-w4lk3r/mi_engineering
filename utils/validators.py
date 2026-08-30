from typing import Optional
from disposable_email_domains import blocklist
from django.core.exceptions import ValidationError


def validate_not_disposable_email(email: Optional[str]) -> None:
    """
    Validates that the provided email address does not belong to a known
    disposable/temporary email provider.
    """
    if not email or "@" not in email:
        return

    domain = email.split("@")[-1].lower().strip()

    if domain in blocklist:
        raise ValidationError(
            "Temporary or disposable email addresses are not allowed. Please use a valid email address.",
            code="disposable_email_not_allowed")
