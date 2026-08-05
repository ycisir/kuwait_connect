from django.urls import URLPattern, path
from core import views

urlpatterns = [
    path('', views.home, name='home'),
    path("businesses/", views.business_list, name="business_list"),
]
