JAZZMIN_SETTINGS = {
    # Branding
    "site_title":
    "M.I. Engineering Admin",
    "site_header":
    "M.I. Engineering Works",
    "site_brand":
    "M.I. Engineering",
    "welcome_sign":
    "Welcome to M.I. Engineering Works Admin Portal",
    "copyright":
    "M.I. Engineering Works",

    # Sidebar
    "show_sidebar":
    True,
    "navigation_expanded":
    True,

    # App & Model Ordering
    "order_with_respect_to": [
        "home",
        "accounts",
        "auth",
    ],

    # FontAwesome Icons for Custom Models
    "icons": {
        "accounts.User": "fas fa-users-cog",
        "auth.Group": "fas fa-user-shield",
        "home.ContactInquiry": "fas fa-envelope-open-text",
    },

    # Top Menu Navigation
    "topmenu_links": [
        {
            "name": "Dashboard",
            "url": "admin:index",
            "permissions": ["auth.view_user"],
        },
        {
            "name": "View Site",
            "url": "/",
            "new_window": True,
        },
    ],

    # UI Cleanup & Customizations
    "hide_apps": [],
    "hide_models": [],
    "show_ui_builder":
    False,
    "changeform_format":
    "horizontal_tabs",
    "related_modal_active":
    True,
}

JAZZMIN_UI_TWEAKS = {
    # Light/White Theme Configuration
    "theme": "flatly",
    "dark_mode_theme": None,

    # Navbar Styling
    "navbar": "navbar-white navbar-light",

    # Sidebar Styling
    "sidebar": "sidebar-light-primary",
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,

    # Brand & Accent Colors
    "brand_colour": "navbar-white",
    "accent": "accent-primary",

    # Button Customization
    "button_classes": {
        "primary": "btn-primary",
        "secondary": "btn-outline-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success",
    },

    # Typography & Sizing
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,
}
