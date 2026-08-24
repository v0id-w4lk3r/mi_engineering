from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy

from accounts.views.mixins import AnonymousRequiredMixin


class UserLoginView(AnonymousRequiredMixin, LoginView):
    template_name = "login.html"

    def get_success_url(self):
        return reverse_lazy("home:index")

    def form_valid(self, form):
        messages.success(self.request,
                         "Welcome back! You have successfully logged in.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request,
                       "Invalid username or password. Please try again.")
        return super().form_invalid(form)
