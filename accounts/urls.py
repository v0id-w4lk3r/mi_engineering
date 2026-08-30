from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    path("login/", views.UserLoginView.as_view(), name="login"),
    path("logout/", views.UserLogoutView.as_view(), name="logout"),
    path("register/", views.UserRegisterView.as_view(), name="register"),
    path("profile/", views.ClientProfileView.as_view(), name="profile"),
    path("password-change/",
         views.CustomPasswordChangeView.as_view(),
         name="password_change"),
    path("password-reset/",
         views.CustomPasswordResetView.as_view(),
         name="password_reset"),
    path("password-reset/confirm/<uidb64>/<token>/",
         views.CustomPasswordResetConfirmView.as_view(),
         name="password_reset_confirm"),
]
