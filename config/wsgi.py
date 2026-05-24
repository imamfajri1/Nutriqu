"""
WSGI config untuk Nutriqu — titik masuk untuk Vercel dan Gunicorn.
"""
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')

application = get_wsgi_application()
app = application  # alias untuk Vercel
