# Changelog

All notable changes to this project are documented in this file.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [Unreleased] — 2026-09-13

### Added

#### SEO Infrastructure
- Installed `django-meta==2.5.1` for structured SEO meta tag management
- Added `django.contrib.sitemaps` to `INSTALLED_APPS`
- Created `home/sitemaps.py` with three sitemap classes:
  - `StaticViewSitemap` — homepage, about, contact (priority 0.8)
  - `ProductSitemap` — all active products with `lastmod` from `updated_at` (priority 0.9)
  - `CategorySitemap` — all active product categories (priority 0.7)
- Wired `/sitemap.xml` endpoint in root `urls.py`
- Added `/robots.txt` endpoint served from `templates/robots.txt` template
- Added `django-meta` configuration block to `settings/base.py`:
  - `META_USE_OG_PROPERTIES = True`
  - `META_USE_TWITTER_PROPERTIES = True`
  - `META_USE_SCHEMAORG_PROPERTIES = True`
  - `META_DEFAULT_KEYWORDS` with industry-specific terms
  - `META_INCLUDE_KEYWORDS_TAG = True`

#### Favicons & Web Manifest
- Replaced placeholder `img/logo/logo.png` favicon links with full `favicon_io/` set in `base.html`:
  - `favicon.ico` (universal fallback)
  - `favicon-16x16.png` and `favicon-32x32.png` (tab icons)
  - `apple-touch-icon.png` (iOS home screen)
  - `site.webmanifest` (PWA manifest)
  - `theme-color` and `msapplication-TileColor` meta tags
- Fixed `static/favicon_io/site.webmanifest`:
  - Populated blank `name` ("M.I. Engineering Works") and `short_name` ("MI Engineering")
  - Fixed icon paths to `/static/favicon_io/`
  - Added `description` and `start_url: "/"`

#### Template SEO Blocks (All Pages)
- **`product_detail.html`**: Added `og:type=product`, OG/Twitter image with fallback,
  `BreadcrumbList` JSON-LD schema, `dateModified`, `manufacturer`, `offers` (with
  `InStock`/`OutOfStock` availability), and `material`/`grade` in Product schema
- **`product_list.html`**: Added `og:type`, `og:image` fallback, `ItemList` +
  `BreadcrumbList` JSON-LD schemas with category awareness
- **`contact.html`**: Added complete SEO from scratch — title, description, keywords,
  canonical, OG tags, `meta_robots: noindex follow`, `ContactPage` + `LocalBusiness`
  JSON-LD schema
- **`gallery_list.html`**: Added complete SEO from scratch — title, description, canonical,
  OG, `CollectionPage` JSON-LD schema
- **`gallery_detail.html`**: Added complete SEO from scratch — title, description, canonical,
  OG image from media, `VideoObject`/`ImageObject` JSON-LD schema (type-aware)
- **`index.html`**: Added canonical, OG, Twitter blocks, and `WebSite` + `Organization`
  JSON-LD schema with Google Sitelinks `SearchAction`
- **`about.html`**: Added `og:type`, OG title/description/image, `Organization` JSON-LD
  schema with `knowsAbout` and `contactPoint`

#### Accessibility
- Added `aria-label="Breadcrumb"` to product breadcrumb `<nav>`
- Added `aria-current="page"` to current product title in breadcrumb
- Added `aria-labelledby` and `role` attributes across homepage and about sections
- Added `aria-hidden="true"` to decorative icons throughout

#### Deployment
- `entrypoint.sh`: Added explicit `makemigrations` for all four apps before `migrate`:
  - `accounts`, `home`, `gallery`, `products`

### Changed

#### `.gitignore`
- Added `*/migrations/*.py` rule to exclude auto-generated migration files from version
  control while preserving `*/migrations/__init__.py` so directories remain tracked

#### `requirements.txt` / `pyproject.toml` / `uv.lock`
- Added `django-meta==2.5.1`

#### `mi_engineering/settings/base.py`
- Added `django.contrib.sitemaps` and `meta` to `INSTALLED_APPS`
- Appended `django-meta` configuration block

#### `mi_engineering/urls.py`
- Registered `sitemap` view at `/sitemap.xml` with all three sitemap classes
- Registered `robots.txt` plain-text template view at `/robots.txt`

#### Homepage Content (`home/templates/partials/home/`)
- **`_hero.html`**: Rewrote H1 to include "Made in India", ISO·DIN·ASTM badge,
  product-specific body copy (materials, size ranges M3–M64, EN 10204),
  `fetchpriority="high"` on LCP hero image, CTA links to `/products/`
- **`_products_overview.html`**: Added DIN/ISO standard references to each product
  category card; added 4-column spec stat bar (size range, SS grades, standards, certs)
- **`_capabilities_standards.html`**: Each standard card now has 3-point bullet list
  of specific products/grades; expanded badge lists with DIN 934, DIN 976, ISO 4017,
  ASTM A490
- **`_industries_process.html`**: Each industry card now contains specific product
  examples (e.g. L/J-type anchor bolts, ASTM A193 B7 studs); process step 04 mentions
  EN 10204 3.1 MTC; added 24hr response mention
- **`_quality_cta.html`**: Added 4 QA certificate badge chips (EN 10204 3.1, Thread
  Gauge, Dimensional Verification, Hardness Testing); fixed CTA links to `/products/`

#### About Page Content (`home/templates/partials/about/`)
- **`_hero.html`**: H1 rewritten as keyword-rich manufacturer title; replaced placeholder
  icon box with 4-stat grid (M3–M64, ISO·DIN·ASTM, SS304·SS316, EN 10204); fixed CTAs
  to link to `/products/`
- **`_who_we_are.html`**: Expanded from 1 vague paragraph to 3 specific paragraphs;
  value badge descriptions made more detailed; layout updated to `items-start`
- **`_capabilities.html`**: Each capability card now has a full description; materials
  listed explicitly (SS304, SS316L, Grade B7, Alloy, MS, Brass)
- **`_industries.html`**: Each industry tile now has a subtitle (e.g. "ASTM A193 B7
  Studs" for Power & Energy, "Anchor Bolts & Tie Rods" for Construction)
- **`_cta.html`**: Added OEM supply agreement paragraph; both CTAs now HTMX-enabled
  with correct links to `/products/` and `/contact-us/`

### Fixed
- `site.webmanifest` had blank `name` and `short_name` fields — fixed
- `contact.html` had no SEO meta blocks whatsoever — fixed
- `gallery_list.html` and `gallery_detail.html` had no SEO meta blocks — fixed
- `index.html` had no canonical, OG, or schema — fixed
- `about/_hero.html` "Explore Products" button pointed to invalid `{% url 'products:list' %}` — fixed to `products:product_list`
- `_quality_cta.html` "Browse Categories" linked to `#products` anchor only — fixed to full `/products/` URL with HTMX
