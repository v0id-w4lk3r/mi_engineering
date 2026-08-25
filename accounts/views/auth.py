from typing import Any
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.db import transaction
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView

from accounts.forms import ClientRegistrationForm
from accounts.models import User
from accounts.views.mixins import AnonymousRequiredMixin


# 1. User Registration View
class UserRegisterView(AnonymousRequiredMixin, CreateView):
    """Handles new client registration, automatic login, and profile signal triggers."""

    form_class = ClientRegistrationForm
    template_name = "register.html"
    success_url = reverse_lazy("home:homepage")

    def form_valid(self, form: ClientRegistrationForm) -> HttpResponse:
        with transaction.atomic():
            user: User = form.save(commit=False)
            user.role = User.Role.CLIENT
            user.save()
            self.object = user

        # Log user in using ModelBackend explicitly
        login(
            self.request,
            user,
            backend="django.contrib.auth.backends.ModelBackend",
        )

        messages.success(
            self.request,
            "Account created successfully! Welcome to M.I. Engineering Works.",
        )
        return redirect(self.get_success_url())

    def form_invalid(self, form: ClientRegistrationForm) -> HttpResponse:
        messages.error(
            self.request,
            "Registration failed. Please fix the highlighted form errors.",
        )
        return super().form_invalid(form)


# 2. User Login View
class UserLoginView(AnonymousRequiredMixin, LoginView):
    """Authenticates existing users and redirects to homepage upon success."""

    template_name = "login.html"

    def get_success_url(self) -> str:
        return str(reverse_lazy("home:homepage"))

    def form_valid(self, form: Any) -> HttpResponse:
        messages.success(self.request,
                         "Welcome back! You have successfully logged in.")
        return super().form_valid(form)

    def form_invalid(self, form: Any) -> HttpResponse:
        messages.error(self.request,
                       "Invalid username or password. Please try again.")
        return super().form_invalid(form)


# 3. User Logout View
class UserLogoutView(LogoutView):
    """Logs out the user and displays a flash feedback message."""

    next_page = reverse_lazy("accounts:login")

    def dispatch(self, request: HttpRequest, *args: Any,
                 **kwargs: Any) -> HttpResponse:
        if request.user.is_authenticated:
            messages.info(request, "You have been logged out successfully.")
        return super().dispatch(request, *args, **kwargs)
