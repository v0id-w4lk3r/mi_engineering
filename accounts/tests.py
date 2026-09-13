from django.contrib.admin.sites import AdminSite
from django.contrib.auth import authenticate, get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from accounts.admin import UserAdmin as CustomUserAdmin
from accounts.models import User

UserModel = get_user_model()


class AuthenticationBackendTests(TestCase):
    def setUp(self):
        self.user = UserModel.objects.create_user(
            username="engineering_lead",
            email="lead@miengineeringworks.in",
            password="SecurePassword123!",
        )

    def test_authenticate_with_username(self):
        user = authenticate(
            request=None,
            username="engineering_lead",
            password="SecurePassword123!",
        )
        self.assertIsNotNone(user)
        self.assertEqual(user.pk, self.user.pk)

    def test_authenticate_with_email(self):
        user = authenticate(
            request=None,
            username="lead@miengineeringworks.in",
            password="SecurePassword123!",
        )
        self.assertIsNotNone(user)
        self.assertEqual(user.pk, self.user.pk)

    def test_authenticate_with_email_case_insensitive(self):
        user = authenticate(
            request=None,
            username="LEAD@miengineeringworks.in",
            password="SecurePassword123!",
        )
        self.assertIsNotNone(user)
        self.assertEqual(user.pk, self.user.pk)

    def test_authenticate_invalid_credentials(self):
        user = authenticate(
            request=None,
            username="lead@miengineeringworks.in",
            password="WrongPassword",
        )
        self.assertIsNone(user)


class UserLoginViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = UserModel.objects.create_user(
            username="client_user",
            email="client@example.com",
            password="ClientPass123!",
        )

    def test_login_redirects_to_next_parameter(self):
        target_url = reverse("home:contact-us") + "?product=Hex+Bolt"
        login_url = f"{reverse('accounts:login')}?next={target_url}"
        response = self.client.post(
            login_url,
            {
                "username": "client@example.com",
                "password": "ClientPass123!",
                "next": target_url,
            },
        )
        self.assertRedirects(response, target_url, fetch_redirect_response=False)

    def test_login_redirects_to_home_by_default(self):
        response = self.client.post(
            reverse("accounts:login"),
            {
                "username": "client_user",
                "password": "ClientPass123!",
            },
        )
        self.assertRedirects(response, reverse("home:homepage"), fetch_redirect_response=False)


class UserAdminTests(TestCase):
    def test_add_fieldsets_includes_email(self):
        site = AdminSite()
        admin_obj = CustomUserAdmin(UserModel, site)
        form_cls = admin_obj.get_form(None, obj=None)
        self.assertIn("email", form_cls.base_fields)

    def test_get_fieldsets_does_not_duplicate_for_add_view(self):
        site = AdminSite()
        admin_obj = CustomUserAdmin(UserModel, site)
        fieldsets = admin_obj.get_fieldsets(None, obj=None)
        titles = [title for title, data in fieldsets if title]
        self.assertEqual(titles.count("Custom Profile Info"), 1)
