from django.templatetags.static import static

UNFOLD = {
    "SITE_TITLE": "M.I. Engineering Admin",
    "SITE_HEADER": "M.I. Engineering Works",
    "SITE_URL": "/",
    "SITE_ICON": {
        "light": lambda request: static("img/logo/logo.png"),  # Light mode
        "dark": lambda request: static("img/logo/logo.png"),  # Dark mode
    },
    "THEME": "light", # Enforce light theme
    "COLORS": {
        "primary": {
            "50": "#f0fdf4",
            "100": "#dcfce7",
            "200": "#bbf7d0",
            "300": "#86efac",
            "400": "#4ade80",
            "500": "#22c55e",
            "600": "#16a34a",
            "700": "#15803d",
            "800": "#166534",
            "900": "#14532d",
        },
    },
}
