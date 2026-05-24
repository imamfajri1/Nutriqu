from django.urls import path
from . import views

urlpatterns = [
    path('log/', views.daily_log_view, name='daily-log'),
    path('log/tambah/', views.add_food_entry_view, name='add-entry'),
    path('log/tambah-banyak/', views.bulk_add_entries_view, name='bulk-add-entries'),
    path('log/<int:pk>/hapus/', views.delete_food_entry_view, name='delete-entry'),
    path('log/recall/', views.food_recall_view, name='food-recall'),
]
