from django.urls import path
from . import views

urlpatterns = [
    path('makanan/cari/', views.food_search_view, name='food-search'),
    path('makanan/scan/', views.nutrition_scan_view, name='food-scan'),
]
