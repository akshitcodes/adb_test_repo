#!/bin/bash
set -euo pipefail

cd /src/rest

exec gunicorn rest.wsgi:application -b 0.0.0.0:8000 --workers 3 --preload --timeout 120 --worker-tmp-dir /dev/shm
