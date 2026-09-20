from typing import TYPE_CHECKING
from django.db import models
from django.utils.text import slugify
from django_ckeditor_5.fields import CKEditor5Field

if TYPE_CHECKING:
    from django.db.models.manager import RelatedManager


class Category(models.Model):
    name = models.CharField(max_length=150, unique=True)
    slug = models.SlugField(max_length=150, unique=True, blank=True)
    description = models.TextField(blank=True, default="")
    image = models.ImageField(upload_to="categories/", blank=True, null=True)
    is_active = models.BooleanField(default=True, db_index=True)

    # SEO fields
    meta_title = models.CharField(
        max_length=255,
        blank=True,
        default="",
        help_text="SEO Meta Title (optional)",
    )
    meta_description = models.TextField(
        blank=True,
        default="",
        help_text="SEO Meta Description (optional)",
    )
    meta_keywords = models.CharField(
        max_length=255,
        blank=True,
        default="",
        help_text="SEO Meta Keywords, comma-separated (optional)",
    )

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ["name"]

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

    def __str__(self):
        return self.name


class Application(models.Model):
    name = models.CharField(max_length=150, unique=True)
    slug = models.SlugField(max_length=150, unique=True, blank=True)
    description = models.TextField(blank=True, default="")
    image = models.ImageField(upload_to="applications/", blank=True, null=True)

    # SEO fields
    meta_title = models.CharField(
        max_length=255,
        blank=True,
        default="",
        help_text="SEO Meta Title (optional)",
    )
    meta_description = models.TextField(
        blank=True,
        default="",
        help_text="SEO Meta Description (optional)",
    )
    meta_keywords = models.CharField(
        max_length=255,
        blank=True,
        default="",
        help_text="SEO Meta Keywords, comma-separated (optional)",
    )

    class Meta:
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name) or "application"
            slug = base_slug
            counter = 1
            while Application.objects.filter(slug=slug).exclude(id=self.id).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Standard(models.Model):
    name = models.CharField(max_length=150, unique=True)
    slug = models.SlugField(max_length=150, unique=True, blank=True)
    description = models.TextField(blank=True, default="")

    # SEO fields
    meta_title = models.CharField(
        max_length=255,
        blank=True,
        default="",
        help_text="SEO Meta Title (optional)",
    )
    meta_description = models.TextField(
        blank=True,
        default="",
        help_text="SEO Meta Description (optional)",
    )
    meta_keywords = models.CharField(
        max_length=255,
        blank=True,
        default="",
        help_text="SEO Meta Keywords, comma-separated (optional)",
    )

    class Meta:
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name) or "standard"
            slug = base_slug
            counter = 1
            while Standard.objects.filter(slug=slug).exclude(id=self.id).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Material(models.Model):
    name = models.CharField(max_length=150, unique=True)
    slug = models.SlugField(max_length=150, unique=True, blank=True)
    description = models.TextField(blank=True, default="")
    image = models.ImageField(upload_to="materials/", blank=True, null=True)

    # SEO fields
    meta_title = models.CharField(
        max_length=255,
        blank=True,
        default="",
        help_text="SEO Meta Title (optional)",
    )
    meta_description = models.TextField(
        blank=True,
        default="",
        help_text="SEO Meta Description (optional)",
    )
    meta_keywords = models.CharField(
        max_length=255,
        blank=True,
        default="",
        help_text="SEO Meta Keywords, comma-separated (optional)",
    )

    class Meta:
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name) or "material"
            slug = base_slug
            counter = 1
            while Material.objects.filter(slug=slug).exclude(id=self.id).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Product(models.Model):
    if TYPE_CHECKING:
        id: int
        images: RelatedManager["ProductImage"]

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="products",
        db_index=True,
    )
    materials = models.ManyToManyField(Material, blank=True, related_name="products")
    applications = models.ManyToManyField(Application, blank=True, related_name="products")
    standards = models.ManyToManyField(Standard, blank=True, related_name="products")
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    short_description = models.CharField(
        max_length=500, help_text="Summary shown on product cards")

    description = CKEditor5Field(
        "Description",
        config_name="extends",
        help_text="Detailed overview with formatting, lists, and images",
    )

    # Common Industrial Attributes
    material = models.CharField(
        max_length=150,
        blank=True,
        default="",
        help_text="e.g. Stainless Steel, Mild Steel, Brass",
    )
    grade = models.CharField(
        max_length=150,
        blank=True,
        default="",
        help_text="e.g. SS304, SS316, Grade 8.8",
    )
    size_range = models.CharField(
        max_length=150,
        blank=True,
        default="",
        help_text="e.g. M3 to M64 / 1/2' to 4'",
    )

    # Technical Data Rich Content
    chemical_composition = CKEditor5Field(
        "Chemical Composition",
        config_name="extends",
        blank=True,
        default="",
        help_text="Chemical breakdown and element percentages",
    )
    mechanical_properties = CKEditor5Field(
        "Mechanical Properties",
        config_name="extends",
        blank=True,
        default="",
        help_text="Tensile strength, yield strength, elongation, and hardness",
    )

    # SEO fields
    meta_title = models.CharField(
        max_length=255,
        blank=True,
        default="",
        help_text="SEO Meta Title (optional)",
    )
    meta_description = models.TextField(
        blank=True,
        default="",
        help_text="SEO Meta Description (optional)",
    )
    meta_keywords = models.CharField(
        max_length=255,
        blank=True,
        default="",
        help_text="SEO Meta Keywords, comma-separated (optional)",
    )

    is_featured = models.BooleanField(default=False, db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["is_active", "is_featured"]),
        ]

    @property
    def primary_image(self):
        """Returns the primary image or falls back to the first uploaded image."""
        if hasattr(self, "_prefetched_objects_cache") and "images" in self._prefetched_objects_cache:
            images = self._prefetched_objects_cache["images"]
            return next((img for img in images if img.is_primary), None) or (images[0] if images else None)
        return self.images.filter(is_primary=True).first() or self.images.first()

    @property
    def display_material(self):
        """Returns comma-separated material names or falls back to the material text."""
        if hasattr(self, "_prefetched_objects_cache") and "materials" in self._prefetched_objects_cache:
            mats = self._prefetched_objects_cache["materials"]
            if mats:
                return ", ".join(m.name for m in mats)
        elif self.pk and self.materials.exists():
            return ", ".join(m.name for m in self.materials.all())
        return self.material or "Industrial Grade"

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Product.objects.filter(slug=slug).exclude(
                    id=self.id).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class ProductImage(models.Model):
    if TYPE_CHECKING:
        id: int

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="images",
    )
    image = models.ImageField(upload_to="products/")
    alt_text = models.CharField(max_length=255, blank=True, default="")
    is_primary = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.is_primary:
            # Ensure only one image is set as primary per product
            ProductImage.objects.filter(
                product=self.product,
                is_primary=True).exclude(id=self.id).update(is_primary=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Image for {self.product.title}"


class ProductSpecification(models.Model):
    if TYPE_CHECKING:
        id: int

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="specifications",
    )
    key = models.CharField(
        max_length=100,
        help_text="Property Name (e.g., Surface Finish)",
    )
    value = models.CharField(
        max_length=255,
        help_text="Property Value (e.g., Galvanized)",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["product", "key"],
                name="unique_product_spec_key",
            )
        ]

    def __str__(self):
        return f"{self.key}: {self.value}"
