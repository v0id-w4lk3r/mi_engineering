from .address import (
    AddressCreateView,
    AddressDeleteView,
    AddressListView,
    AddressUpdateView,
)
from .auth import UserLoginView, UserLogoutView, UserRegisterView
from .password_management import (
    CustomPasswordChangeView,
    CustomPasswordResetConfirmView,
    CustomPasswordResetView
)
from .profile import ClientProfileView

__all__ = [
    "UserLoginView",
    "UserLogoutView",
    "UserRegisterView",
    "CustomPasswordChangeView",
    "CustomPasswordResetView",
    "CustomPasswordResetConfirmView",
    "ClientProfileView",
    "AddressListView",
    "AddressCreateView",
    "AddressUpdateView",
    "AddressDeleteView",
]
