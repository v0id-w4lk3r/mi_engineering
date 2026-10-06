from typing import Any
from django.conf import settings
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.views.generic import View

from home.forms import ContactForm
from products.models import Product
from utils.emails import send_app_email


class ProductInquiryView(View):
    """
    Handles inline HTMX RFQ inquiries directly from the product details page.
    Validates buyer name, email, and requirements message without redirects.
    """

    def post(self, request: HttpRequest, slug: str) -> HttpResponse:
        product = get_object_or_404(Product, slug=slug, is_active=True)
        form = ContactForm(request.POST)

        if form.is_valid():
            inquiry = form.save(commit=False)
            if request.user.is_authenticated:
                inquiry.user = request.user
            inquiry.save()

            # Dispatch notification email to industrial sales
            import email.utils
            raw_from = getattr(settings, "DEFAULT_FROM_EMAIL", "")
            admin_email: str = email.utils.parseaddr(raw_from)[1] or getattr(
                settings, "EMAIL_HOST_USER", "miengineering17@gmail.com"
            )

            send_app_email(
                subject=f"New Product Inquiry: {product.title} - {inquiry.full_name}",
                recipient_list=[admin_email],
                template_name="emails/contact_inquiry",
                context={
                    "full_name": inquiry.full_name,
                    "email": inquiry.email,
                    "message": inquiry.message,
                },
                fail_silently=True,
            )

            # Auto-reply acknowledgment to client
            send_app_email(
                subject=f"Inquiry Received: {product.title} - M.I. Engineering Works",
                recipient_list=[inquiry.email],
                template_name="emails/contact_receipt",
                context={
                    "full_name": inquiry.full_name,
                    "message": inquiry.message,
                },
                fail_silently=True,
            )

            return render(
                request,
                "partials/details/_inquiry_success.html",
                {
                    "product": product,
                    "inquiry": inquiry,
                },
            )

        # Form contains validation errors
        return render(
            request,
            "partials/details/_inquiry_form.html",
            {
                "product": product,
                "form": form,
            },
        )
