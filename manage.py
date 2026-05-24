"""Titik masuk Django untuk perintah manajemen."""
import os
import sys


def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Tidak dapat mengimpor Django. Pastikan virtualenv sudah diaktifkan "
            "dan Django sudah terinstal."
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
