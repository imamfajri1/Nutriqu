"""
Konfigurasi URL utama Nutriqu.
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect


def redirect_to_dashboard(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return redirect('login')


urlpatterns = [
    path('admin/', admin.site.urls),

    # Redirect root ke dashboard atau login
    path('', redirect_to_dashboard, name='home'),

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
