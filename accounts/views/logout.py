from django.contrib import messages
from django.contrib.auth.views import LogoutView
from django.urls import reverse_lazy


class UserLogoutView(LogoutView):
    next_page = reverse_lazy("accounts:login")

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.info(request, "You have been logged out successfully.")
        return super().dispatch(request, *args, **kwargs)
