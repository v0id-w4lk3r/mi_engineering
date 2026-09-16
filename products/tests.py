from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from products.models import Application, Category, Product, ProductImage, Standard


class ProductModelTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(
            name="Industrial Fasteners",
            description="All types of fasteners",
        )

    def test_category_slug_generation_and_uniqueness(self):
        self.assertEqual(self.category.slug, "industrial-fasteners")
        # Name "Industrial-Fasteners" slugifies to the same base slug
        cat2 = Category.objects.create(name="Industrial-Fasteners")
        self.assertEqual(cat2.slug, "industrial-fasteners-1")

    def test_product_slug_generation_and_uniqueness(self):
        p1 = Product.objects.create(
            category=self.category,
            title="High Tensile Hex Bolt",
            short_description="Grade 8.8 Hex Bolt",
            material="Carbon Steel",
        )
        self.assertEqual(p1.slug, "high-tensile-hex-bolt")

        p2 = Product.objects.create(
            category=self.category,
            title="High Tensile Hex Bolt",
            short_description="Another batch",
            material="Carbon Steel",
        )
        self.assertEqual(p2.slug, "high-tensile-hex-bolt-1")

    def test_primary_image_with_prefetched_cache_zero_queries(self):
        product = Product.objects.create(
            category=self.category,
            title="Stainless Steel Washer",
            short_description="SS304 Washer",
            material="Stainless Steel",
        )
        dummy_img = SimpleUploadedFile("test.jpg", b"image_data", content_type="image/jpeg")
        img1 = ProductImage.objects.create(product=product, image=dummy_img, is_primary=False)
        img2 = ProductImage.objects.create(product=product, image=dummy_img, is_primary=True)

        # Query using prefetch_related
        p = Product.objects.prefetch_related("images").get(id=product.id)
        with self.assertNumQueries(0):
            primary = p.primary_image
            self.assertIsNotNone(primary)
            self.assertEqual(primary.id, img2.id)
            self.assertTrue(primary.is_primary)

    def test_primary_image_fallback_to_first_image(self):
        product = Product.objects.create(
            category=self.category,
            title="Plain Rivet",
            short_description="Rivet without primary tag",
            material="Aluminum",
        )
        dummy_img = SimpleUploadedFile("rivet.jpg", b"image_data", content_type="image/jpeg")
        img = ProductImage.objects.create(product=product, image=dummy_img, is_primary=False)

        self.assertEqual(product.primary_image.id, img.id)

    def test_primary_image_none_when_no_images(self):
        product = Product.objects.create(
            category=self.category,
            title="Imageless Bolt",
            short_description="No images yet",
            material="Steel",
        )
        self.assertIsNone(product.primary_image)

    def test_single_primary_image_enforcement(self):
        product = Product.objects.create(
            category=self.category,
            title="Flange Nut",
            short_description="Nut with flange",
            material="Steel",
        )
        dummy_img = SimpleUploadedFile("nut.jpg", b"image_data", content_type="image/jpeg")
        img1 = ProductImage.objects.create(product=product, image=dummy_img, is_primary=True)
        img2 = ProductImage.objects.create(product=product, image=dummy_img, is_primary=True)

        img1.refresh_from_db()
        self.assertFalse(img1.is_primary)
        self.assertTrue(img2.is_primary)


class ProductListViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.cat_fasteners = Category.objects.create(name="Fasteners")
        self.cat_pipes = Category.objects.create(name="Pipes & Fittings")

        self.prod_active1 = Product.objects.create(
            category=self.cat_fasteners,
            title="Stainless Hex Bolt",
            short_description="SS Hex Bolt",
            material="Stainless Steel",
            is_active=True,
        )
        self.prod_active2 = Product.objects.create(
            category=self.cat_pipes,
            title="Seamless Steel Pipe",
            short_description="ASTM A106 pipe",
            material="Carbon Steel",
            is_active=True,
        )
        self.prod_inactive = Product.objects.create(
            category=self.cat_fasteners,
            title="Discontinued Screw",
            short_description="Obsolete",
            material="Iron",
            is_active=False,
        )

    def test_list_displays_only_active_products(self):
        url = reverse("products:product_list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        products = list(response.context["products"])
        self.assertIn(self.prod_active1, products)
        self.assertIn(self.prod_active2, products)
        self.assertNotIn(self.prod_inactive, products)

    def test_filter_by_category_slug(self):
        url = reverse("products:category_product_list", kwargs={"category_slug": self.cat_fasteners.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        products = list(response.context["products"])
        self.assertIn(self.prod_active1, products)
        self.assertNotIn(self.prod_active2, products)

    def test_search_query_filter(self):
        url = reverse("products:product_list")
        response = self.client.get(url, {"q": "Seamless"})
        self.assertEqual(response.status_code, 200)
        products = list(response.context["products"])
        self.assertEqual(len(products), 1)
        self.assertEqual(products[0], self.prod_active2)

    def test_active_products_count_annotation(self):
        url = reverse("products:product_list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        categories = {c.id: c.active_products_count for c in response.context["categories"]}
        # cat_fasteners has 1 active, 1 inactive -> count must be 1
        self.assertEqual(categories[self.cat_fasteners.id], 1)
        # cat_pipes has 1 active -> count must be 1
        self.assertEqual(categories[self.cat_pipes.id], 1)

    def test_htmx_partial_grid_rendering(self):
        url = reverse("products:product_list")
        response = self.client.get(
            url,
            HTTP_HX_REQUEST="true",
            HTTP_HX_TARGET="catalog-content",
        )
        self.assertEqual(response.status_code, 200)
        # Verify rendered template is the partial grid, not the full layout
        self.assertTemplateUsed(response, "partials/list/_product_grid.html")
        self.assertTemplateNotUsed(response, "base.html")


class ProductDetailViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.category = Category.objects.create(name="Precision Valves")
        self.product = Product.objects.create(
            category=self.category,
            title="High Pressure Ball Valve",
            short_description="Class 800 valve",
            material="Forged Steel",
            chemical_composition="<p><strong>Carbon:</strong> 0.25% max</p>",
            mechanical_properties="<p><strong>Tensile:</strong> 485 MPa</p>",
            is_active=True,
        )

    def test_product_detail_renders_tabs_safely(self):
        url = reverse("products:product_detail", kwargs={"slug": self.product.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Carbon:</strong> 0.25% max")
        self.assertContains(response, "Tensile:</strong> 485 MPa")

    def test_inactive_product_returns_404(self):
        self.product.is_active = False
        self.product.save()
        url = reverse("products:product_detail", kwargs={"slug": self.product.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)


class ApplicationAndStandardSEOTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.application = Application.objects.create(
            name="Aerospace Engineering",
            description="Components for aerospace and aviation.",
            meta_title="Aerospace Fasteners & Parts | M.I. Engineering Works",
            meta_description="High-precision aerospace fasteners certified to critical specs.",
            meta_keywords="aerospace fasteners, aviation components, mil-spec hardware",
        )
        self.standard = Standard.objects.create(
            name="ISO 4014",
            description="Hexagon head bolts - Product grades A and B.",
            meta_title="ISO 4014 Hex Bolts Specification | M.I. Engineering Works",
            meta_description="Conforming to ISO 4014 standard for precision hexagon head bolts.",
            meta_keywords="ISO 4014, DIN 931, hex head bolts ISO standard",
        )
        self.category = Category.objects.create(
            name="Fasteners",
            meta_title="Industrial Fasteners Supplier | M.I. Engineering Works",
            meta_description="Top manufacturer of standard and custom industrial fasteners.",
            meta_keywords="fasteners supplier, precision bolts, industrial screws",
        )
        self.product = Product.objects.create(
            category=self.category,
            title="ISO 4014 Aerospace Hex Bolt",
            short_description="Certified ISO 4014 bolt for aerospace",
            material="Titanium",
            meta_title="Titanium ISO 4014 Aerospace Bolt | M.I. Engineering Works",
            meta_description="Titanium aerospace hex bolt compliant with ISO 4014 standards.",
            meta_keywords="titanium bolt, ISO 4014 aerospace, high-strength fastener",
            is_active=True,
        )
        self.product.applications.add(self.application)
        self.product.standards.add(self.standard)

    def test_application_list_seo_meta_tags(self):
        url = reverse("products:application_list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Industrial Fastener & Component Applications | M.I. Engineering Works")
        self.assertContains(response, "Explore industrial fastener and component applications")
        self.assertContains(response, "industrial applications, fastener applications")

    def test_standard_list_seo_meta_tags(self):
        url = reverse("products:standard_list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "International Manufacturing Standards & Specifications | M.I. Engineering Works")
        self.assertContains(response, "Browse industrial fasteners and engineering components")
        self.assertContains(response, "manufacturing standards, ISO fasteners")

    def test_application_product_list_custom_meta_tags(self):
        url = reverse("products:application_product_list", kwargs={"application_slug": self.application.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Aerospace Fasteners &amp; Parts | M.I. Engineering Works")
        self.assertContains(response, self.application.meta_description)
        self.assertContains(response, self.application.meta_keywords)

    def test_standard_product_list_custom_meta_tags(self):
        url = reverse("products:standard_product_list", kwargs={"standard_slug": self.standard.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.standard.meta_title)
        self.assertContains(response, self.standard.meta_description)
        self.assertContains(response, self.standard.meta_keywords)

    def test_category_product_list_custom_meta_tags(self):
        url = reverse("products:category_product_list", kwargs={"category_slug": self.category.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.category.meta_title)
        self.assertContains(response, self.category.meta_description)
        self.assertContains(response, self.category.meta_keywords)

    def test_product_detail_custom_meta_tags(self):
        url = reverse("products:product_detail", kwargs={"slug": self.product.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.product.meta_title)
        self.assertContains(response, self.product.meta_description)
        self.assertContains(response, self.product.meta_keywords)

    def test_product_admin_category_dropdown_and_seo_fieldsets(self):
        from django.contrib.admin.sites import site
        from products.admin import ProductAdmin, ApplicationAdmin, StandardAdmin
        admin_instance = ProductAdmin(Product, site)
        # raw_id_fields must NOT contain 'category' so that it renders as a dropdown
        self.assertNotIn("category", getattr(admin_instance, "raw_id_fields", ()))
        
        # Verify SEO fieldsets are defined
        app_admin = ApplicationAdmin(Application, site)
        app_fieldsets = [f[0] for f in app_admin.get_fieldsets(None)]
        self.assertIn("SEO & Meta Tags", app_fieldsets)

        std_admin = StandardAdmin(Standard, site)
        std_fieldsets = [f[0] for f in std_admin.get_fieldsets(None)]
        self.assertIn("SEO & Meta Tags", std_fieldsets)

        prod_fieldsets = [f[0] for f in admin_instance.get_fieldsets(None)]
        self.assertIn("SEO & Meta Tags", prod_fieldsets)

    def test_sitemap_includes_applications_and_standards(self):
        url = reverse("django.contrib.sitemaps.views.sitemap")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        self.assertIn(f"/products/applications/{self.application.slug}/", content)
        self.assertIn(f"/products/standards/{self.standard.slug}/", content)
        self.assertIn("/products/applications/", content)
        self.assertIn("/products/standards/", content)
