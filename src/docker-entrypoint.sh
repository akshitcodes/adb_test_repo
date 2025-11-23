#!/bin/bash
set -euo pipefail

cd /src/rest

# Start gunicorn (3 workers by default)
exec gunicorn rest.wsgi:application -b 0.0.0.0:8000 --workers 3
