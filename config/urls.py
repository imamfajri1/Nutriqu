"""
Konfigurasi URL utama Nutriqu.
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import render, redirect


def home_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'pages/landing.html')


urlpatterns = [
    path('admin/', admin.site.urls),

    # Landing page (unauthenticated) atau redirect ke dashboard
    path('', home_view, name='home'),

    # Accounts
    path('', include('apps.accounts.urls')),

    # Foods
    path('', include('apps.foods.urls')),

    # Tracking
    path('', include('apps.tracking.urls')),

    # Nutrition
    path('', include('apps.nutrition.urls')),
]

# Serve static files di development (fallback selain WhiteNoise)
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
