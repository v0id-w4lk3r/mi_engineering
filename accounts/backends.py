from typing import Any
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q
from django.http import HttpRequest


class EmailOrUsernameModelBackend(ModelBackend):
    """
    Authenticates against settings.AUTH_USER_MODEL using either
    the username or the email address (case-insensitive).
    """

    def authenticate(
        self,
        request: HttpRequest | None,
        username: str | None = None,
        password: str | None = None,
        **kwargs: Any,
    ) -> Any:
        UserModel = get_user_model()
        if username is None:
            username = kwargs.get(UserModel.USERNAME_FIELD)

        if not username or not password:
            return None

        user = (
            UserModel._default_manager.filter(
                Q(username__iexact=username) | Q(email__iexact=username)
            ).first()
        )

        if user and user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
