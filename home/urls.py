from django.urls import path
from .views import (
    HomePageView,
    AboutView,
    ContactView,
    TermsOfServiceView,
    PrivacyPolicyView,
)

app_name = "home"

urlpatterns = [
    path("", HomePageView.as_view(), name="homepage"),
    path("about-us/", AboutView.as_view(), name="about-us"),
    path("contact-us/", ContactView.as_view(), name="contact-us"),
    path("terms-of-service/",
         TermsOfServiceView.as_view(),
         name="terms-of-service"),
    path("privacy-policy/", PrivacyPolicyView.as_view(),
         name="privacy-policy"),
]
