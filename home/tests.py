import tempfile
from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.messages.storage.fallback import FallbackStorage
from django.core import mail
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, RequestFactory, TestCase, override_settings
from django.urls import reverse

from home.admin import ContactInquiryAdmin
from home.forms.admin_forms import CustomGroupAdminForm
from home.models import ContactInquiry

UserModel = get_user_model()


class CustomGroupAdminFormTests(TestCase):
    def setUp(self):
        self.content_type = ContentType.objects.get_for_model(Group)
        self.permission = Permission.objects.filter(content_type=self.content_type).first()

    def test_save_commit_true_assigns_permissions(self):
        app_label = self.permission.content_type.app_label
        field_name = f"perm_app_{app_label}"
        data = {
            "name": "Managers",
            field_name: [self.permission.id],
        }
        form = CustomGroupAdminForm(data=data)
        self.assertTrue(form.is_valid(), form.errors)
        group = form.save(commit=True)
        self.assertIsNotNone(group.pk)
        self.assertTrue(group.permissions.filter(id=self.permission.id).exists())

    def test_save_commit_false_defers_m2m(self):
        app_label = self.permission.content_type.app_label
        field_name = f"perm_app_{app_label}"
        data = {
            "name": "Supervisors",
            field_name: [self.permission.id],
        }
        form = CustomGroupAdminForm(data=data)
        self.assertTrue(form.is_valid(), form.errors)
        group = form.save(commit=False)
        self.assertIsNone(group.pk)

        # Calling save_m2m after persisting instance saves permissions correctly
        group.save()
        form.save_m2m()
        self.assertTrue(group.permissions.filter(id=self.permission.id).exists())


class ContactInquiryAdminTests(TestCase):
    def setUp(self):
        self.site = AdminSite()
        self.admin = ContactInquiryAdmin(ContactInquiry, self.site)
        self.factory = RequestFactory()

    def _get_request_with_messages(self):
        request = self.factory.post("/")
        setattr(request, "session", {})
        messages = FallbackStorage(request)
        setattr(request, "_messages", messages)
        return request

    def test_client_info_summary_anonymous(self):
        inquiry = ContactInquiry(full_name="Jane Doe", email="jane@example.com", message="Hi")
        summary = self.admin.client_info_summary(inquiry)
        self.assertEqual(summary, "Anonymous User / No registered account")

    def test_client_info_summary_authenticated_user(self):
        user = UserModel.objects.create_user(
            username="client1",
            email="client1@company.com",
            password="Password123!",
            company_name="Apex Industries",
            phone_number="+919876543210",
            role=UserModel.Role.CLIENT,
        )
        inquiry = ContactInquiry(user=user, full_name="Client One", email="client1@company.com")
        summary = self.admin.client_info_summary(inquiry)
        self.assertIn("Company: Apex Industries", summary)
        self.assertIn("Phone: +919876543210", summary)
        self.assertIn("Registered Email: client1@company.com", summary)

    def test_save_model_sends_reply_email_with_attachment(self):
        inquiry = ContactInquiry.objects.create(
            full_name="Procurement Officer",
            email="procurement@example.com",
            message="Looking for 500 bolts.",
        )
        attachment = SimpleUploadedFile(
            "quotation.txt",
            b"Price quotation details...",
            content_type="text/plain",
        )
        inquiry.reply_message = "<p>Here is your quote.</p>"
        inquiry.reply_attachment = attachment

        request = self._get_request_with_messages()

        class DummyForm:
            changed_data = ["reply_message", "reply_attachment"]

        with tempfile.TemporaryDirectory() as temp_media:
            with override_settings(MEDIA_ROOT=temp_media):
                self.admin.save_model(request, inquiry, DummyForm(), change=True)
                inquiry.refresh_from_db()
                self.assertTrue(inquiry.is_processed)
                self.assertIsNotNone(inquiry.replied_at)
                self.assertEqual(len(mail.outbox), 1)
                sent_mail = mail.outbox[0]
                self.assertEqual(sent_mail.to, ["procurement@example.com"])
                self.assertEqual(len(sent_mail.attachments), 1)

    def test_admin_has_attachment_and_attachment_preview(self):
        inquiry_without = ContactInquiry.objects.create(
            full_name="User Without File",
            email="nofile@example.com",
            message="No file attached",
        )
        self.assertFalse(self.admin.has_attachment(inquiry_without))
        self.assertEqual(self.admin.attachment_preview(inquiry_without), "No file attached")

        file_obj = SimpleUploadedFile("drawing.pdf", b"%PDF-1.4 dummy", content_type="application/pdf")
        inquiry_with = ContactInquiry.objects.create(
            full_name="User With File",
            email="withfile@example.com",
            message="File attached",
            attachment=file_obj,
        )
        self.assertTrue(self.admin.has_attachment(inquiry_with))
        preview = self.admin.attachment_preview(inquiry_with)
        self.assertIn("drawing", preview)
        self.assertIn(".pdf", preview)
        self.assertIn("View / Download", preview)


class ContactViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = UserModel.objects.create_user(
            username="reguser",
            first_name="Alice",
            last_name="Smith",
            email="alice@company.com",
            password="SecurePassword123!",
        )

    def test_get_initial_with_product_query_params(self):
        url = reverse("home:contact-us")
        response = self.client.get(url, {"product": "Heavy Hex Bolt", "material": "SS316", "grade": "8.8"})
        self.assertEqual(response.status_code, 200)
        form = response.context["form"]
        message_initial = form.initial.get("message", "")
        self.assertIn("Heavy Hex Bolt", message_initial)
        self.assertIn("Material: SS316", message_initial)
        self.assertIn("Grade: 8.8", message_initial)

    def test_get_initial_with_authenticated_user(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("home:contact-us"))
        self.assertEqual(response.status_code, 200)
        form = response.context["form"]
        self.assertEqual(form.initial.get("email"), "alice@company.com")
        self.assertEqual(form.initial.get("full_name"), "Alice Smith")

    def test_post_anonymous_contact_inquiry(self):
        url = reverse("home:contact-us")
        data = {
            "full_name": "Bob Builder",
            "email": "bob@example.com",
            "message": "Inquiring about heavy machinery parts.",
        }
        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        inquiry = ContactInquiry.objects.filter(email="bob@example.com").first()
        self.assertIsNotNone(inquiry)
        self.assertIsNone(inquiry.user)
        self.assertEqual(inquiry.full_name, "Bob Builder")
        # 2 emails should be dispatched: admin notification & customer receipt
        self.assertEqual(len(mail.outbox), 2)
        recipients = {m.to[0] for m in mail.outbox}
        self.assertIn("bob@example.com", recipients)

    def test_post_authenticated_contact_inquiry_links_user(self):
        self.client.force_login(self.user)
        url = reverse("home:contact-us")
        data = {
            "full_name": "Alice Smith",
            "email": "alice@company.com",
            "message": "Custom fabrication order inquiry.",
        }
        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        inquiry = ContactInquiry.objects.filter(email="alice@company.com").first()
        self.assertIsNotNone(inquiry)
        self.assertEqual(inquiry.user, self.user)

    def test_post_contact_inquiry_with_excel_upload(self):
        url = reverse("home:contact-us")
        excel_file = SimpleUploadedFile(
            "bom_quote.xlsx",
            b"fake excel content",
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        data = {
            "full_name": "Charlie Engineer",
            "email": "charlie@machinery.com",
            "message": "Attached is our bill of materials in Excel format.",
            "attachment": excel_file,
        }
        with tempfile.TemporaryDirectory() as temp_media:
            with override_settings(MEDIA_ROOT=temp_media):
                response = self.client.post(url, data, follow=True)
                self.assertEqual(response.status_code, 200)
                inquiry = ContactInquiry.objects.filter(email="charlie@machinery.com").first()
                self.assertIsNotNone(inquiry)
                self.assertTrue(bool(inquiry.attachment))
                self.assertTrue(inquiry.attachment.name.endswith(".xlsx"))
                # Check email sent with attachment to admin
                self.assertEqual(len(mail.outbox), 2)
                admin_email = mail.outbox[0]
                self.assertEqual(len(admin_email.attachments), 1)

    def test_post_contact_inquiry_with_drawing_upload(self):
        url = reverse("home:contact-us")
        drawing_file = SimpleUploadedFile(
            "flange_blueprint.dwg",
            b"fake cad dwg binary data",
            content_type="application/acad",
        )
        data = {
            "full_name": "Dana Drafter",
            "email": "dana@cadworks.com",
            "message": "Please review the attached DWG product drawing.",
            "attachment": drawing_file,
        }
        with tempfile.TemporaryDirectory() as temp_media:
            with override_settings(MEDIA_ROOT=temp_media):
                response = self.client.post(url, data, follow=True)
                self.assertEqual(response.status_code, 200)
                inquiry = ContactInquiry.objects.filter(email="dana@cadworks.com").first()
                self.assertIsNotNone(inquiry)
                self.assertTrue(bool(inquiry.attachment))
                self.assertTrue(inquiry.attachment.name.endswith(".dwg"))

    def test_post_contact_inquiry_rejects_disallowed_extension(self):
        url = reverse("home:contact-us")
        malicious_file = SimpleUploadedFile(
            "script.exe",
            b"fake executable",
            content_type="application/x-msdownload",
        )
        data = {
            "full_name": "Eve Hacker",
            "email": "eve@security.com",
            "message": "Here is a script.",
            "attachment": malicious_file,
        }
        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        inquiry = ContactInquiry.objects.filter(email="eve@security.com").first()
        self.assertIsNone(inquiry)
        self.assertIn("form", response.context)
        form = response.context["form"]
        self.assertTrue(form.errors.get("attachment"))

    def test_post_contact_inquiry_rejects_oversized_file(self):
        url = reverse("home:contact-us")
        huge_file = SimpleUploadedFile(
            "large_cad.step",
            b"0" * (26 * 1024 * 1024),
            content_type="application/step",
        )
        data = {
            "full_name": "Frank Huge",
            "email": "frank@bigfiles.com",
            "message": "Huge STEP model.",
            "attachment": huge_file,
        }
        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        inquiry = ContactInquiry.objects.filter(email="frank@bigfiles.com").first()
        self.assertIsNone(inquiry)
        form = response.context["form"]
        self.assertTrue(form.errors.get("attachment"))
        self.assertIn("25 MB", str(form.errors.get("attachment")))

