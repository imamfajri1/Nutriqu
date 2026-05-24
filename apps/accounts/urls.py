from django.urls import path
from . import views

urlpatterns = [
    path('daftar/', views.register_view, name='register'),
    path('masuk/', views.login_view, name='login'),
    path('keluar/', views.logout_view, name='logout'),
    path('profil/', views.profile_view, name='profile'),
    path('profil/imt/tambah/', views.imt_create_view, name='imt-add'),
]
