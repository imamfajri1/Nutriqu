from django.urls import path
from . import views

urlpatterns = [
    # Pencarian (semua user)
    path('makanan/cari/', views.food_search_view, name='food-search'),
    path('makanan/scan/', views.nutrition_scan_view, name='food-scan'),

    # Manajemen makanan (ahli gizi / superuser)
    path('makanan/kelola/', views.food_manage_view, name='food-manage'),
    path('makanan/tambah/', views.food_add_view, name='food-add'),
    path('makanan/<int:pk>/edit/', views.food_edit_view, name='food-edit'),
    path('makanan/<int:pk>/hapus/', views.food_delete_view, name='food-delete'),
]
