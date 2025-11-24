"""
WSGI config for rest project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/howto/deployment/wsgi/
"""

import os
import logging

# Ensure settings module is available early
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rest.settings')

logger = logging.getLogger(__name__)


def _maybe_wait_for_db():
	"""Wait for MongoDB during process startup if enabled.

	Controlled by `RUN_DB_WAIT` env var (default '1'). Timeout can be
	overridden with `DB_WAIT_TIMEOUT` (seconds).
	"""
	if os.environ.get('RUN_DB_WAIT', '1') == '0':
		logger.debug('RUN_DB_WAIT=0, skipping DB wait')
		return

	try:
		timeout = int(os.environ.get('DB_WAIT_TIMEOUT', '120'))
	except ValueError:
		timeout = 120

	try:
		# Import here so django settings are configured
		import django

		django.setup()
		from rest.db import wait_for_db

		logger.info('Waiting for MongoDB (timeout=%ds)...', timeout)
		wait_for_db(timeout_seconds=timeout)
		logger.info('MongoDB ready')
	except Exception:
		logger.exception('Failed waiting for MongoDB during startup')
		# Re-raise so the process fails fast and orchestration can handle it
		raise


# perform DB wait at module import time (WSGI startup)
_maybe_wait_for_db()

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
