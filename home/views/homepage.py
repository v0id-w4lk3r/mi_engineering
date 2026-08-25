from typing import Any, Dict
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


class ContactView(FormView):
    template_name = "contact.html"
    form_class = ContactForm
    success_url = reverse_lazy("home:contact-us")

    def form_valid(self, form: ContactForm) -> HttpResponse:
        # Save submission to Database
        inquiry = form.save()

        # Send email notification
        admin_email: str = getattr(settings, "DEFAULT_FROM_EMAIL",
                                   "sales@miengineering.com")
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

        messages.success(
            self.request,
            "Thank you for reaching out! Your inquiry has been logged and sent to our team.",
        )
        return super().form_valid(form)

    def form_invalid(self, form: ContactForm) -> HttpResponse:
        messages.error(
            self.request,
            "There was an error processing your submission. Please check the form field errors below.",
        )
        return self.render_to_response(self.get_context_data(form=form))
