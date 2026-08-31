from django.db import models
from django.utils.text import slugify
from django_ckeditor_5.fields import CKEditor5Field


class Category(models.Model):
    name = models.CharField(max_length=150, unique=True)
    slug = models.SlugField(max_length=150, unique=True, blank=True)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to="categories/", blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(Category,
                                 on_delete=models.CASCADE,
                                 related_name="products")
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    short_description = models.CharField(
        max_length=500, help_text="Summary shown on product cards")

    # Rich Text Editor Field for detailed descriptions
    description = CKEditor5Field(
        "Description",
        config_name="extends",
        help_text="Detailed overview with formatting, lists, and images",
    )

    # Common Industrial Attributes
    material = models.CharField(
        max_length=150, help_text="e.g. Stainless Steel, Mild Steel, Brass")
    grade = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        help_text="e.g. SS304, SS316, Grade 8.8",
    )
    standard = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        help_text="e.g. ISO 9001, DIN 933, ASTM A193",
    )
    size_range = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        help_text="e.g. M3 to M64 / 1/2' to 4'",
    )

    # Structured Technical Data (JSON)
    chemical_composition = models.JSONField(
        default=dict,
        blank=True,
        help_text=
        'JSON format, e.g., {"Carbon (C)": "0.08%", "Chromium (Cr)": "18.00%"}',
    )
    mechanical_properties = models.JSONField(
        default=dict,
        blank=True,
        help_text=
        'JSON format, e.g., {"Tensile Strength": "515 MPa", "Yield Strength": "205 MPa"}',
    )

    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class ProductImage(models.Model):
    product = models.ForeignKey(Product,
                                on_delete=models.CASCADE,
                                related_name="images")
    image = models.ImageField(upload_to="products/")
    alt_text = models.CharField(max_length=255, blank=True, null=True)
    is_primary = models.BooleanField(default=False)

    def __str__(self):
        return f"Image for {self.product.title}"


class ProductSpecification(models.Model):
    """Dynamic key-value technical specs (e.g., Tensile Strength: 800 MPa)"""

    product = models.ForeignKey(Product,
                                on_delete=models.CASCADE,
                                related_name="specifications")
    key = models.CharField(max_length=100,
                           help_text="Property Name (e.g., Surface Finish)")
    value = models.CharField(
        max_length=255,
        help_text="Property Value (e.g., Galvanized / Mirror Polish)",
    )

    def __str__(self):
        return f"{self.key}: {self.value}"
