from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("get_item_cost", )

    @admin.display(description="Subtotal")
    def get_item_cost(self, obj: OrderItem) -> str:
        return f"INR {obj.get_cost():.2f}"


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "order_number",
        "user",
        "status",
        "payment_status",
        "total_amount",
        "created_at",
    )
    list_editable = ("status", "payment_status")
    list_filter = ("status", "payment_status", "created_at")
    search_fields = (
        "order_number",
        "user__username",
        "user__email",
        "shipping_address__recipient_name",
        "shipping_address__city",
    )
    inlines = [OrderItemInline]
    readonly_fields = ("order_number", "subtotal", "total_amount")

    fieldsets = (
        ("Order Context", {
            "fields": ("order_number", "user", "shipping_address")
        }),
        ("Fulfillment & Payment Controls", {
            "fields": ("status", "payment_status")
        }),
        ("Financial Totals", {
            "fields": ("subtotal", "shipping_cost", "total_amount")
        }),
        ("Logistics & Documents", {
            "fields": (
                "shipping_method",
                "courier_name",
                "tracking_number",
                "tracking_url",
                "estimated_delivery",
                "dispatched_at",
                "invoice",
            )
        }),
    )
