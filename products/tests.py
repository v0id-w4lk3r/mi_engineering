from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from products.models import Category, Product, ProductImage


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
