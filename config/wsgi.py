"""
WSGI config untuk Nutriqu — titik masuk untuk Vercel dan Gunicorn.
Auto-migrate pada startup agar skema DB selalu sinkron tanpa perlu build step.
"""
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')

# Jalankan migration pending sebelum app dimulai.
# Diperlukan di Vercel karena buildCommand tidak reliable untuk @vercel/python.
def _run_pending_migrations():
    try:
        from django.db import connection
        from django.db.migrations.executor import MigrationExecutor
        executor = MigrationExecutor(connection)
        plan = executor.migration_plan(executor.loader.graph.leaf_nodes())
        if plan:
            from django.core.management import call_command
            call_command('migrate', '--no-input', verbosity=0)
    except Exception:
        pass  # Jangan crash app jika migrate gagal (misal: DB tidak tersedia)

_run_pending_migrations()

application = get_wsgi_application()
app = application  # alias untuk Vercel
