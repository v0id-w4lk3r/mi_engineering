from typing import TYPE_CHECKING, Any, Dict
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.views.generic import TemplateView

from accounts.forms import UserProfileForm
from home.models import ContactInquiry

if TYPE_CHECKING:
    from accounts.models import User


class ClientProfileView(LoginRequiredMixin, TemplateView):
    """
    Dashboard View for registered account holders.
    Handles user profile updates and past RFQ inquiry tracking.
    """

    template_name = "profile.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        user: "User" = self.request.user  # type: ignore

        enquiries_queryset = ContactInquiry.objects.filter(
            user=user).order_by("-created_at")

        context.update({
            "enquiries":
            enquiries_queryset,
            "total_enquiries_count":
            enquiries_queryset.count(),
            "profile_form":
            kwargs.get("profile_form") or UserProfileForm(instance=user),
        })
        return context

    def post(self, request: HttpRequest, *args: Any,
             **kwargs: Any) -> HttpResponse:
        form = UserProfileForm(request.POST, instance=request.user)

        if form.is_valid():
            form.save()
            messages.success(
                request,
                "Your profile details have been updated successfully.",
            )

            if request.headers.get("HX-Request"):
                return render(
                    request,
                    "partials/profile_form.html",
                    {"profile_form": form},
                )

            return redirect("accounts:profile")

        messages.error(request,
                       "Please fix the errors in your profile details.")

        if request.headers.get("HX-Request"):
            return render(
                request,
                "partials/profile_form.html",
                {"profile_form": form},
            )

        context = self.get_context_data(profile_form=form)
        return render(request, self.template_name, context)
