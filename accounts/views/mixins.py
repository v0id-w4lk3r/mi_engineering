from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import HttpRequest
from django.shortcuts import redirect

from accounts.models import User


class BaseAccessMixin(UserPassesTestMixin):
    """Base mixin providing explicit type annotations for Pylance."""
    request: HttpRequest


class AnonymousRequiredMixin(BaseAccessMixin):
    """Prevents authenticated users from viewing registration and login pages."""
    def test_func(self) -> bool:
        return not self.request.user.is_authenticated

    def handle_no_permission(self):
        return redirect("home:index")


class ClientRequiredMixin(BaseAccessMixin):
    """Restricts view access strictly to registered Clients."""
    def test_func(self) -> bool:
        user = self.request.user
        if isinstance(user, User):
            return user.is_client()
        return False

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return redirect("accounts:login")
        messages.error(self.request, "Access restricted to client accounts.")
        return redirect("home:index")


class StaffRequiredMixin(BaseAccessMixin):
    """Restricts view access to Staff/Engineers and Admins."""
    def test_func(self) -> bool:
        user = self.request.user
        if isinstance(user, User):
            return user.is_staff_member()
        return False

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return redirect("accounts:login")
        messages.error(self.request, "Access restricted to authorized staff members.")
        return redirect("home:index")


class AdminRequiredMixin(BaseAccessMixin):
    """Restricts view access exclusively to Admins."""
    def test_func(self) -> bool:
        user = self.request.user
        if isinstance(user, User):
            return user.role == User.Role.ADMIN
        return False

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return redirect("accounts:login")
        messages.error(self.request, "Administrator privileges required.")
        return redirect("home:index")