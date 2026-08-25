from typing import Any, Dict
from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.views.generic import TemplateView

from accounts.forms import ClientProfileForm
from accounts.views.mixins import ClientRequiredMixin


class ClientProfileView(ClientRequiredMixin, TemplateView):
    """Unified Profile view for registered clients to manage details and view orders."""

    template_name = "profile.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        user = self.request.user
        profile = getattr(user, "client_profile", None)

        # Retrieves orders safely if an order relationship exists on the User model
        orders = getattr(user, "orders", None)
        orders_queryset = orders.all().prefetch_related(
            "items") if orders else []

        context.update({
            "profile": profile,
            "orders": orders_queryset,
            "profile_form": ClientProfileForm(instance=profile),
        })
        return context

    def post(self, request: HttpRequest, *args: Any,
             **kwargs: Any) -> HttpResponse:
        profile = getattr(request.user, "client_profile", None)
        form = ClientProfileForm(request.POST, instance=profile)

        if form.is_valid():
            form.save()
            messages.success(
                request,
                "Your profile details have been updated successfully.")
            return redirect("accounts:profile")

        context = self.get_context_data()
        context["profile_form"] = form
        messages.error(request, "Please fix the errors in your profile form.")
        return render(request, self.template_name, context)
