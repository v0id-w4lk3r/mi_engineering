from django.db import models


class Category(models.Model):
    """Category model for grouping gallery media items."""

    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120,
                            unique=True,
                            help_text="URL-friendly identifier")
    description = models.TextField(blank=True)
    display_order = models.PositiveIntegerField(
        default=0, help_text="Lower numbers appear first")

    class Meta:
        ordering = ["display_order", "name"]
        verbose_name = "Category"
        verbose_name_plural = "Categories"

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

    @property
    def media_type_label(self) -> str:
        """Type-safe getter for the media type display label."""
        return str(self.MediaType(self.media_type).label)

    def __str__(self) -> str:
        return f"{self.title} ({self.media_type_label})"
