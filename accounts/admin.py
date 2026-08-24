from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from accounts.models import User


class ClientRegistrationForm(UserCreationForm):

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email", "company_name", "phone_number")


class UserRegisterView(CreateView):
    form_class = ClientRegistrationForm
    template_name = "accounts/register.html"
    success_url = reverse_lazy("home:index")

    def form_valid(self, form):
        user = form.save(commit=False)
        user.role = User.Role.CLIENT  # Hardcode role to CLIENT
        user.save()
        login(self.request, user)
        messages.success(self.request, "Account created successfully!")
        return redirect(str(self.get_success_url()))
