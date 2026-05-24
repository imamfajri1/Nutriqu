"""
Pengaturan untuk environment development — SQLite, DEBUG aktif.
"""
from .base import *

DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Whitenoise tetap aktif di dev agar static files tersedia tanpa runserver --insecure
WHITENOISE_USE_FINDERS = True
