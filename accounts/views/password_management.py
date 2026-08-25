from typing import Any
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import (
    PasswordChangeView,
    PasswordResetConfirmView,
    PasswordResetView,
)
from django.http import HttpResponse
from django.urls import reverse_lazy
from accounts.views.mixins import AnonymousRequiredMixin


# 1. Password Change 
class CustomPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    """
    Allows authenticated users to change their password.
    Protected by LoginRequiredMixin to prevent anonymous access.
    """

    template_name = "password_change.html"
    success_url = reverse_lazy("home:homepage")

    def form_valid(self, form: Any) -> HttpResponse:
        messages.success(self.request,
                         "Your password was updated successfully.")
        return super().form_valid(form)


# 2. Password Reset Request 
class CustomPasswordResetView(AnonymousRequiredMixin, PasswordResetView):
    """
    Step 1 of password reset flow.
    Restricted to anonymous (logged-out) users via AnonymousRequiredMixin.
    """

    template_name = "password_reset.html"
    email_template_name = "emails/password_reset_email.html"
    subject_template_name = "emails/password_reset_subject.txt"
    success_url = reverse_lazy("accounts:login")

    def form_valid(self, form: Any) -> HttpResponse:
        response = super().form_valid(form)
        messages.info(
            self.request,
            "If an account exists with that email address, password reset instructions have been sent.",
        )
        return response


# 3. Password Reset Confirm 
class CustomPasswordResetConfirmView(AnonymousRequiredMixin,
                                     PasswordResetConfirmView):
    """
    Step 2 of password reset flow where user inputs a new password.
    Restricted to anonymous users using AnonymousRequiredMixin.
    """

    template_name = "password_reset_confirm.html"
    success_url = reverse_lazy("accounts:login")

    def form_valid(self, form: Any) -> HttpResponse:
        response = super().form_valid(form)
        messages.success(
            self.request,
            "Your password has been reset successfully. You can now log in with your new credentials.",
        )
        return response
