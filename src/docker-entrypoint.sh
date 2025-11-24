#!/bin/bash
set -euo pipefail

cd /src/rest


python - <<'PY'
import os
import django

# Ensure Django settings module is set before accessing django.conf.settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rest.settings')
django.setup()

from rest.db import wait_for_db
try:
	# Allow overriding timeout via DB_WAIT_TIMEOUT env var (seconds)
	timeout = int(os.environ.get('DB_WAIT_TIMEOUT', '60'))
	wait_for_db(timeout=timeout)
except Exception as e:
	# If DB never becomes available, fail fast so container health checks catch it
	print(f"ERROR: waiting for MongoDB failed: {e}")
	raise
PY
exec gunicorn rest.wsgi:application -b 0.0.0.0:8000 --workers 3 --preload --timeout 120 --worker-tmp-dir /dev/shm
