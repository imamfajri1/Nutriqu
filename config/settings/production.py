"""
Pengaturan untuk environment production — PostgreSQL via Supabase, DEBUG nonaktif.
"""
from .base import *
from decouple import config

DEBUG = False

ALLOWED_HOSTS = config(
    'ALLOWED_HOSTS',
    default='.vercel.app,localhost,127.0.0.1',
    cast=lambda v: [s.strip() for s in v.split(',')],
)

# Wajib untuk HTMX POST requests di HTTPS (Django 4.0+)
CSRF_TRUSTED_ORIGINS = config(
    'CSRF_TRUSTED_ORIGINS',
    default='https://*.vercel.app',
    cast=lambda v: [s.strip() for s in v.split(',')],
)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST'),
        'PORT': config('DB_PORT', default='5432'),
        'OPTIONS': {
            'sslmode': 'require',
        },
        'CONN_MAX_AGE': 60,
    }
}

STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'

SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_SSL_REDIRECT = config('SECURE_SSL_REDIRECT', default=True, cast=bool)
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
