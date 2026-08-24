from django.urls import path
from . import views

app_name = 'home'

urlpatterns = [
    path('', views.HomePageView.as_view(), name='homepage'),
    path('about-us/', views.AboutView.as_view(), name='about-us'),
    path('contact-us/', views.ContactView.as_view(), name='contact-us'),
]