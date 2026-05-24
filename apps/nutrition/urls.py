from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('laporan/', views.weekly_report_view, name='weekly-report'),
    path('gizi/ringkasan/', views.nutrition_summary_view, name='nutrition-summary'),
]
