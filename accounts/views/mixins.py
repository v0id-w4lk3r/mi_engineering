from typing import TYPE_CHECKING
from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect

from accounts.models import User

if TYPE_CHECKING:
    from django.views import View
    _BaseMixin = View
else:
    _BaseMixin = object


class BaseAccessMixin(UserPassesTestMixin):
    """Base mixin providing explicit type annotations for Pylance."""
    request: HttpRequest


class AnonymousRequiredMixin(_BaseMixin):
    """Prevents authenticated users from viewing registration and login pages."""

    def dispatch(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if request.user.is_authenticated:
            return redirect("home:homepage")
        return super().dispatch(request, *args, **kwargs)


class ClientRequiredMixin(BaseAccessMixin):
    """Restricts view access strictly to registered Clients."""

    def test_func(self) -> bool:
        user = self.request.user
        return isinstance(user, User) and user.is_client()

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return redirect("accounts:login")
        messages.error(self.request, "Access restricted to client accounts.")
        return redirect("home:homepage")


class StaffRequiredMixin(BaseAccessMixin):
    """Restricts view access to Staff/Engineers and Admins."""

    def test_func(self) -> bool:
        user = self.request.user
        return isinstance(user, User) and user.is_staff_member()

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return redirect("accounts:login")
        messages.error(self.request,
                       "Access restricted to authorized staff members.")
        return redirect("home:homepage")


class AdminRequiredMixin(BaseAccessMixin):
    """Restricts view access exclusively to Admins."""

    def test_func(self) -> bool:
        user = self.request.user
        return isinstance(user, User) and user.role == User.Role.ADMIN

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return redirect("accounts:login")
        messages.error(self.request, "Administrator privileges required.")
        return redirect("home:homepage")
