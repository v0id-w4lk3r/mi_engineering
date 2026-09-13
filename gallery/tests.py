from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from gallery.models import Category, GalleryItem


class GalleryCategoryModelTests(TestCase):
    def test_category_slug_auto_generation_and_uniqueness(self):
        cat1 = Category.objects.create(name="CNC Machinery")
        self.assertEqual(cat1.slug, "cnc-machinery")

        cat2 = Category.objects.create(name="CNC-Machinery")
        self.assertEqual(cat2.slug, "cnc-machinery-1")


class GalleryItemModelTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Factory Tour")
        self.dummy_image = SimpleUploadedFile("plant.jpg", b"img_data", content_type="image/jpeg")

    def test_clean_image_type_requires_image(self):
        item = GalleryItem(
            title="Plant Overview",
            category=self.category,
            media_type=GalleryItem.MediaType.IMAGE,
        )
        with self.assertRaises(ValidationError) as ctx:
            item.clean()
        self.assertIn("image", ctx.exception.message_dict)

    def test_clean_video_type_requires_video_or_video_url(self):
        item = GalleryItem(
            title="Lathe Operation",
            category=self.category,
            media_type=GalleryItem.MediaType.VIDEO,
        )
        with self.assertRaises(ValidationError) as ctx:
            item.clean()
        self.assertIn("video", ctx.exception.message_dict)

    def test_clean_video_type_with_url_validates(self):
        item = GalleryItem(
            title="Lathe Operation",
            category=self.category,
            media_type=GalleryItem.MediaType.VIDEO,
            video_url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        )
        try:
            item.clean()
        except ValidationError:
            self.fail("clean() raised ValidationError unexpectedly for valid video item!")

    def test_embed_url_conversion(self):
        item = GalleryItem(title="Demo")

        # YouTube standard link
        item.video_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        self.assertEqual(item.embed_url, "https://www.youtube-nocookie.com/embed/dQw4w9WgXcQ")

        # YouTube short link
        item.video_url = "https://youtu.be/dQw4w9WgXcQ"
        self.assertEqual(item.embed_url, "https://www.youtube-nocookie.com/embed/dQw4w9WgXcQ")

        # YouTube embed link preserved
        item.video_url = "https://www.youtube-nocookie.com/embed/dQw4w9WgXcQ"
        self.assertEqual(item.embed_url, "https://www.youtube-nocookie.com/embed/dQw4w9WgXcQ")

        # Vimeo standard link
        item.video_url = "https://vimeo.com/123456789"
        self.assertEqual(item.embed_url, "https://player.vimeo.com/video/123456789")

        # None / empty
        item.video_url = None
        self.assertIsNone(item.embed_url)


class GalleryViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.cat_infra = Category.objects.create(name="Infrastructure")
        self.cat_products = Category.objects.create(name="Products")

        self.dummy_image = SimpleUploadedFile("item.jpg", b"img_data", content_type="image/jpeg")

        self.item_image = GalleryItem.objects.create(
            title="Factory Workshop",
            category=self.cat_infra,
            media_type=GalleryItem.MediaType.IMAGE,
            image=self.dummy_image,
            is_active=True,
        )
        self.item_video = GalleryItem.objects.create(
            title="Milling Process",
            category=self.cat_products,
            media_type=GalleryItem.MediaType.VIDEO,
            video_url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            is_active=True,
        )
        self.item_inactive = GalleryItem.objects.create(
            title="Archived Layout",
            category=self.cat_infra,
            media_type=GalleryItem.MediaType.IMAGE,
            image=self.dummy_image,
            is_active=False,
        )

    def test_gallery_list_active_only(self):
        url = reverse("gallery:gallery_list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        items = list(response.context["items"])
        self.assertIn(self.item_image, items)
        self.assertIn(self.item_video, items)
        self.assertNotIn(self.item_inactive, items)

    def test_gallery_list_filter_category(self):
        url = reverse("gallery:gallery_list")
        response = self.client.get(url, {"category": self.cat_infra.slug})
        self.assertEqual(response.status_code, 200)
        items = list(response.context["items"])
        self.assertIn(self.item_image, items)
        self.assertNotIn(self.item_video, items)

    def test_gallery_list_filter_media_type(self):
        url = reverse("gallery:gallery_list")
        response = self.client.get(url, {"type": GalleryItem.MediaType.VIDEO})
        self.assertEqual(response.status_code, 200)
        items = list(response.context["items"])
        self.assertIn(self.item_video, items)
        self.assertNotIn(self.item_image, items)

    def test_gallery_detail_active(self):
        url = reverse("gallery:gallery_detail", kwargs={"pk": self.item_video.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "youtube-nocookie.com/embed/dQw4w9WgXcQ")

    def test_gallery_detail_inactive_404(self):
        url = reverse("gallery:gallery_detail", kwargs={"pk": self.item_inactive.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
