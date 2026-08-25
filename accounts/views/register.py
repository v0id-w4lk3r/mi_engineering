from django.contrib import messages
from django.contrib.auth import login
from django.db import transaction
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView

from accounts.forms import ClientRegistrationForm
from accounts.models import User
from accounts.views.mixins import AnonymousRequiredMixin


class UserRegisterView(AnonymousRequiredMixin, CreateView):
    form_class = ClientRegistrationForm
    template_name = "register.html"
    success_url = reverse_lazy("home:homepage")

    def form_valid(self, form):
        with transaction.atomic():
            user = form.save(commit=False)
            user.role = User.Role.CLIENT
            user.save()
            self.object = user

        # Log the user in with explicit backend specified
        login(self.request,
              user,
              backend="django.contrib.auth.backends.ModelBackend")

        messages.success(
            self.request,
            "Account created successfully! Welcome to M.I. Engineering Works.")
        return redirect(self.get_success_url())

    def form_invalid(self, form):
        messages.error(
            self.request,
            "Registration failed. Please fix the highlighted form errors.")
        return super().form_invalid(form)
