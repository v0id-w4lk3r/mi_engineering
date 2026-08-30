from typing import Any
from django.conf import settings
from django.contrib import messages
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import FormView, TemplateView

from utils.emails import send_app_email
from ..forms import ContactForm


class HomePageView(TemplateView):
    template_name = "index.html"


class AboutView(TemplateView):
    template_name = "about.html"


class TermsOfServiceView(TemplateView):
    template_name = "terms_of_service.html"


class PrivacyPolicyView(TemplateView):
    template_name = "privacy_policy.html"


class ContactView(FormView):
    template_name = "contact.html"
    form_class = ContactForm
    success_url = reverse_lazy("home:contact-us")

    def get_initial(self) -> dict[str, Any]:
        initial = super().get_initial()

        # Capture URL parameter inputs from product detail page redirect
        product = self.request.GET.get("product")
        material = self.request.GET.get("material")
        grade = self.request.GET.get("grade")

        if product:
            specs = []
            if material:
                specs.append(f"Material: {material}")
            if grade:
                specs.append(f"Grade: {grade}")

            spec_details = f" ({', '.join(specs)})" if specs else ""

            # Pre-fill the contact message field
            initial["message"] = (
                f"I am interested in receiving a quote for: {product}{spec_details}.\n\n"
                f"Please provide pricing, delivery timeline, and minimum order quantity."
            )

        return initial

    def form_valid(self, form: ContactForm) -> HttpResponse:
        inquiry = form.save()

        admin_email: str = getattr(settings, "DEFAULT_FROM_EMAIL",
                                   "webmaster@localhost")

        send_app_email(
            subject=f"New Contact Inquiry: {inquiry.full_name}",
            recipient_list=[admin_email],
            template_name="emails/contact_inquiry",
            context={
                "full_name": inquiry.full_name,
                "email": inquiry.email,
                "message": inquiry.message,
            },
            fail_silently=True,
        )

        send_app_email(
            subject="We received your message - M.I. Engineering Works",
            recipient_list=[inquiry.email],
            template_name="emails/contact_receipt",
            context={
                "full_name": inquiry.full_name,
                "message": inquiry.message,
            },
            fail_silently=True,
        )

        messages.success(
            self.request,
            "Thank you for reaching out! Your inquiry has been received and our team will get back to you shortly.",
        )
        return super().form_valid(form)

    def form_invalid(self, form: ContactForm) -> HttpResponse:
        messages.error(
            self.request,
            "There was an error processing your submission. Please check the fields below.",
        )
        return super().form_invalid(form)
