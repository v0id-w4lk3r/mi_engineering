from urllib.parse import parse_qs, urlparse
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.text import slugify


class Category(models.Model):
    """Category model for grouping gallery media items."""

    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120,
                            unique=True,
                            blank=True,
                            help_text="URL-friendly identifier")
    description = models.TextField(blank=True)
    display_order = models.PositiveIntegerField(
        default=0, help_text="Lower numbers appear first")

    class Meta:
        ordering = ["display_order", "name"]
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name) or "category"
            slug = base_slug
            counter = 1
            while Category.objects.filter(slug=slug).exclude(id=self.id).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.name


class GalleryItem(models.Model):
    """Model for managing gallery images and videos uploaded via Admin."""

    class MediaType(models.TextChoices):
        IMAGE = "IMAGE", "Image"
        VIDEO = "VIDEO", "Video"

    title = models.CharField(max_length=255,
                             help_text="Title or caption for the media item")
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="gallery_items",
    )
    media_type = models.CharField(
        max_length=10,
        choices=MediaType.choices,
        default=MediaType.IMAGE,
        help_text="Select whether this item is an image or a video",
    )

    # File handling
    image = models.ImageField(upload_to="gallery/images/",
                              blank=True,
                              null=True)
    video = models.FileField(
        upload_to="gallery/videos/",
        blank=True,
        null=True,
        help_text="Upload MP4/WebM file or use external video URL below",
    )
    video_url = models.URLField(
        blank=True,
        null=True,
        help_text="Optional YouTube or Vimeo embed URL",
    )

    description = models.TextField(blank=True,
                                   help_text="Optional detailed explanation")
    display_order = models.PositiveIntegerField(
        default=0, help_text="Lower numbers appear first")
    is_active = models.BooleanField(
        default=True, help_text="Uncheck to hide from public site")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["display_order", "-uploaded_at"]
        verbose_name = "Gallery Item"
        verbose_name_plural = "Gallery Items"

    def clean(self):
        super().clean()
        if self.media_type == self.MediaType.IMAGE and not self.image:
            raise ValidationError({"image": "An image file is required for items with media type Image."})
        if self.media_type == self.MediaType.VIDEO and not self.video and not self.video_url:
            raise ValidationError({"video": "Either a video file or a video URL is required for Video items."})

    @property
    def embed_url(self) -> str | None:
        """Converts YouTube or Vimeo watch links into valid embed URLs."""
        if not self.video_url:
            return None

        url = self.video_url.strip()
        parsed = urlparse(url)

        # YouTube formats
        if "youtube.com" in parsed.netloc:
            qs = parse_qs(parsed.query)
            video_id = qs.get("v", [None])[0]
            if video_id:
                return f"https://www.youtube-nocookie.com/embed/{video_id}"
            if "/embed/" in parsed.path:
                return url
        elif "youtu.be" in parsed.netloc:
            video_id = parsed.path.lstrip("/")
            if video_id:
                return f"https://www.youtube-nocookie.com/embed/{video_id}"

        # Vimeo formats
        if "vimeo.com" in parsed.netloc and "/video/" not in parsed.path:
            video_id = parsed.path.strip("/")
            if video_id.isdigit():
                return f"https://player.vimeo.com/video/{video_id}"

        return url

    @property
    def media_type_label(self) -> str:
        """Type-safe getter for the media type display label."""
        return self.get_media_type_display()

    def __str__(self) -> str:
        return f"{self.title} ({self.media_type_label})"
