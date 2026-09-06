from typing import Any
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import View

from accounts.models import Address
from orders.models import Order, OrderItem
from products.models import Product


class CheckoutView(LoginRequiredMixin, View):
    """View to display the checkout page with product parameters and saved user addresses."""

    template_name = "checkout.html"

    def get(self, request: HttpRequest, *args: Any,
            **kwargs: Any) -> HttpResponse:
        product_id = request.GET.get("product_id")
        product = get_object_or_404(Product, id=product_id, is_active=True)

        try:
            quantity = int(
                request.GET.get("quantity",
                                getattr(product, "min_order_quantity", 1)))
        except (ValueError, TypeError):
            quantity = getattr(product, "min_order_quantity", 1)

        selected_material = request.GET.get("material",
                                            getattr(product, "material", ""))
        selected_grade = request.GET.get("grade",
                                         getattr(product, "grade", ""))
        unit_price = getattr(product, "unit_price", None) or getattr(
            product, "price", 0)
        total_price = unit_price * quantity

        # Fetch addresses saved under the current user's profile
        saved_addresses = Address.objects.filter(user=request.user)

        context = {
            "product": product,
            "quantity": quantity,
            "selected_material": selected_material,
            "selected_grade": selected_grade,
            "total_price": total_price,
            "saved_addresses": saved_addresses,
        }
        return render(request, self.template_name, context)


class CreateOrderView(LoginRequiredMixin, View):
    """View to handle direct order creation linked to an accounts.Address instance."""

    def post(self, request: HttpRequest, *args: Any,
             **kwargs: Any) -> HttpResponse:
        product_id = request.POST.get("product_id")
        product = get_object_or_404(Product, id=product_id, is_active=True)

        try:
            quantity = int(
                request.POST.get("quantity",
                                 getattr(product, "min_order_quantity", 1)))
        except (ValueError, TypeError):
            quantity = getattr(product, "min_order_quantity", 1)

        material = request.POST.get("material",
                                    getattr(product, "material", ""))
        grade = request.POST.get("grade", getattr(product, "grade", ""))
        unit_price = getattr(product, "unit_price", None) or getattr(
            product, "price", 0)

        selected_address_id = request.POST.get(
            "shipping_address_id") or request.POST.get("address_id")

        if selected_address_id and selected_address_id != "new":
            # Fetch existing address directly owned by the user
            shipping_address = get_object_or_404(
                Address,
                id=selected_address_id,
                user=request.user,
            )
        elif request.POST.get("street_address"):
            # Create a new address linked to the user
            shipping_address = Address.objects.create(
                user=request.user,
                recipient_name=request.POST.get(
                    "recipient_name",
                    request.user.get_full_name()  # type: ignore
                    or request.user.username,
                ),
                street_address=request.POST.get("street_address", ""),
                city=request.POST.get("city", ""),
                state=request.POST.get("state", ""),
                postal_code=request.POST.get("postal_code", ""),
                country=request.POST.get("country", "India"),
                phone_number=request.POST.get("phone_number", ""),
                is_default=not Address.objects.filter(
                    user=request.user).exists(),
            )
        else:
            # Fallback to default address, or the most recent address
            shipping_address = (
                Address.objects.filter(user=request.user,
                                       is_default=True).first()
                or Address.objects.filter(user=request.user).first())

        # Create Order Instance
        order = Order.objects.create(
            user=request.user,
            status=Order.Status.PENDING,
            payment_status=Order.PaymentStatus.PENDING,
            shipping_address=shipping_address,
        )

        # Create OrderItem
        OrderItem.objects.create(
            order=order,
            product=product,
            product_name=product.title,
            material=material,
            grade=grade,
            quantity=quantity,
            unit_price=unit_price,
        )

        messages.success(
            request,
            f"Order #{order.order_number} for '{product.title}' created successfully!",
        )
        return redirect("accounts:profile")


class CancelOrderView(LoginRequiredMixin, View):
    """View to cancel an existing pending order."""

    def post(self, request: HttpRequest, order_id: int, *args: Any,
             **kwargs: Any) -> HttpResponse:
        order = get_object_or_404(Order, id=order_id, user=request.user)

        if order.status in [Order.Status.PENDING, Order.Status.PROCESSING]:
            order.status = Order.Status.CANCELLED
            order.save(update_fields=["status"])
            messages.success(
                request, f"Order #{order.order_number} has been cancelled.")
        else:
            messages.error(request, "This order can no longer be cancelled.")

        return redirect("accounts:profile")
