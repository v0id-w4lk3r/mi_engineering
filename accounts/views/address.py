from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from ..models import Address, User


class ClientProfileView(LoginRequiredMixin, UpdateView):
    """Handles updating basic client information and listing user data."""
    model = User
    fields = ["company_name", "phone_number"]
    template_name = "accounts/profile.html"
    success_url = reverse_lazy("accounts:profile")

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["addresses"] = self.request.user.addresses.all(  # type: ignore
        )
        return context


class AddressListView(LoginRequiredMixin, ListView):
    """Displays a list of saved shipping addresses for the logged-in user."""
    model = Address
    template_name = "accounts/address_list.html"
    context_object_name = "addresses"

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)


class AddressCreateView(LoginRequiredMixin, CreateView):
    """Allows a user to add a new shipping address."""
    model = Address
    fields = [
        "recipient_name",
        "phone_number",
        "street_address",
        "city",
        "state",
        "postal_code",
        "country",
        "is_default",
    ]
    template_name = "accounts/address_form.html"
    success_url = reverse_lazy("accounts:profile")

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, "Address added successfully.")
        return super().form_valid(form)


class AddressUpdateView(LoginRequiredMixin, UpdateView):
    """Allows a user to edit an existing shipping address securely."""
    model = Address
    fields = [
        "recipient_name",
        "phone_number",
        "street_address",
        "city",
        "state",
        "postal_code",
        "country",
        "is_default",
    ]
    template_name = "accounts/address_form.html"
    success_url = reverse_lazy("accounts:profile")

    def get_queryset(self):
        # Security: restrict updates strictly to the owner's addresses
        return Address.objects.filter(user=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, "Address updated successfully.")
        return super().form_valid(form)


class AddressDeleteView(LoginRequiredMixin, DeleteView):
    """Allows a user to delete a saved shipping address."""
    model = Address
    template_name = "accounts/address_confirm_delete.html"
    success_url = reverse_lazy("accounts:profile")

    def get_queryset(self):
        # Security: restrict deletions strictly to the owner's addresses
        return Address.objects.filter(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Address deleted successfully.")
        return super().delete(request, *args, **kwargs)
