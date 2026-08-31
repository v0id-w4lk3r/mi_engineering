from typing import Any, Dict
from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.views.generic import TemplateView

from accounts.forms import ClientProfileForm
from accounts.views.mixins import ClientRequiredMixin


class ClientProfileView(ClientRequiredMixin, TemplateView):
    """
    Unified Dashboard & Profile View for registered clients.
    Handles profile updates and retrieves past orders, RFQs, and product enquiries.
    """

    template_name = "profile.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        user = self.request.user
        profile = getattr(user, "client_profile", None)

        # 1. Retrieve Orders (Prefetching items & products for efficient template rendering)
        orders_rel = getattr(user, "orders", None)
        orders_queryset = (
            orders_rel.select_related("shipping_address").prefetch_related(
                "items__product").order_by("-created_at")
            if orders_rel else [])

        # 2. Retrieve Product Enquiries / Quotation Requests (RFQs)
        # Tries standard related names for enquiries or quotes attached to the user
        enquiries_rel = getattr(user, "enquiries", None) or getattr(
            user, "quotes", None)
        enquiries_queryset = (
            enquiries_rel.select_related("product").order_by("-created_at")
            if enquiries_rel else [])

        # 3. Calculate Summary Metrics for Dashboard Cards
        total_orders_count = len(orders_queryset) if isinstance(
            orders_queryset, list) else orders_queryset.count()
        total_enquiries_count = len(enquiries_queryset) if isinstance(
            enquiries_queryset, list) else enquiries_queryset.count()

        context.update({
            "profile": profile,
            "orders": orders_queryset,
            "enquiries": enquiries_queryset,
            "total_orders_count": total_orders_count,
            "total_enquiries_count": total_enquiries_count,
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

            # Return partial template if submitted via HTMX
            if request.headers.get("HX-Request"):
                context = self.get_context_data()
                context["profile_form"] = form
                return render(request, "partials/profile_form.html",
                              context)

            return redirect("accounts:profile")

        # Form contains validation errors
        messages.error(request,
                       "Please fix the errors in your profile details.")
        context = self.get_context_data()
        context["profile_form"] = form

        if request.headers.get("HX-Request"):
            return render(request, "partials/profile_form.html",
                          context)

        return render(request, self.template_name, context)
