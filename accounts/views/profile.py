from typing import TYPE_CHECKING, Any, Dict
from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.views.generic import TemplateView

from accounts.forms import AddressForm, ClientProfileForm
from accounts.models import Address
from accounts.views.mixins import ClientRequiredMixin
from home.models import ContactInquiry
from orders.models import Order

if TYPE_CHECKING:
    from accounts.models import User


class ClientProfileView(ClientRequiredMixin, TemplateView):
    """
    Unified Dashboard & Profile View for registered clients.
    Handles profile updates, saved addresses, past orders, and product inquiries.
    """

    template_name = "profile.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        user: "User" = self.request.user  # type: ignore

        profile = getattr(user, "client_profile", None)
        addresses = user.addresses.all()

        orders_queryset = (Order.objects.filter(
            user=user).select_related("shipping_address").prefetch_related(
                "items__product").order_by("-created_at"))

        enquiries_queryset = ContactInquiry.objects.filter(
            user=user).order_by("-created_at")

        context.update({
            "profile": profile,
            "addresses": addresses,
            "orders": orders_queryset,
            "enquiries": enquiries_queryset,
            "total_orders_count": orders_queryset.count(),
            "total_enquiries_count": enquiries_queryset.count(),
            "profile_form": ClientProfileForm(instance=profile),
            "address_form": AddressForm(),
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

            if request.headers.get("HX-Request"):
                context = self.get_context_data()
                context["profile_form"] = form
                return render(request, "partials/profile_form.html", context)

            return redirect("accounts:profile")

        messages.error(request,
                       "Please fix the errors in your profile details.")
        context = self.get_context_data()
        context["profile_form"] = form

        if request.headers.get("HX-Request"):
            return render(request, "partials/profile_form.html", context)

        return render(request, self.template_name, context)
