"""Database connection and configuration module."""
import logging
import time
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from django.conf import settings

logger = logging.getLogger(__name__)


class MongoDBClient:
    """Singleton MongoDB client wrapper with lazy connection."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        
        self.mongo_uri = settings.MONGO_URI
        self.client = None
        self.db = None
        self._initialized = True

    def _connect(self):
        """Establish connection to MongoDB (lazy connection on first use)."""
        if self.client is not None:
            return
        
        try:
            self.client = MongoClient(
                self.mongo_uri,
                serverSelectionTimeoutMS=5000,
                socketTimeoutMS=5000,
                retryWrites=False,
                # Connection pool settings
                maxPoolSize=50,
                minPoolSize=10,
            )
            # Trigger connection to check if server is reachable
            self.client.admin.command('ping')
            self.db = self.client['todos_db']
            logger.info("MongoDB connected successfully")
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise

    def get_db(self):
        """Return the database instance."""
        if self.db is None:
            self._connect()
        return self.db

    def close(self):
        """Close the connection."""
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")

    def health_check(self):
        """Check if MongoDB is healthy."""
        try:
            self.get_db().command('ping')
            return True
        except Exception as e:
            logger.warning(f"MongoDB health check failed: {e}")
            return False


# Singleton instance
_mongo_client = None


def get_db():
    """Get or create MongoDB client singleton and return database."""
    global _mongo_client
    if _mongo_client is None:
        _mongo_client = MongoDBClient()
    return _mongo_client.get_db()


def get_mongo_client():
    """Get the MongoDB client wrapper."""
    global _mongo_client
    if _mongo_client is None:
        _mongo_client = MongoDBClient()
    return _mongo_client


def wait_for_db(timeout: int = 30, interval: float = 1.0, timeout_seconds: int = None):
    """Block until MongoDB is available or raise TimeoutError.

    Accepts either `timeout` or `timeout_seconds` for backward/forward
    compatibility with different callers.

    Args:
        timeout: total seconds to wait before giving up.
        interval: seconds between retries.
        timeout_seconds: alias for `timeout` (if provided it overrides `timeout`).
    """
    # allow callers to pass either name
    if timeout_seconds is not None:
        timeout = int(timeout_seconds)

    start = time.time()
    logger.info("Waiting for MongoDB to become available...")

    # Use a short-lived client for probing so we don't depend on the
    # singleton state while the app is booting.
    mongo_uri = getattr(settings, 'MONGO_URI', None)
    if not mongo_uri:
        # fallback to sensible default when settings are not present yet
        import os

        mongo_uri = os.environ.get('MONGO_URI', 'mongodb://mongo:27017')

  
    try:
        import socket

        # extract host from URI (handles simple mongodb://host:port/ cases)
        host_part = mongo_uri.split('://', 1)[-1].split('/', 1)[0]
        host = host_part.split(',', 1)[0].split(':', 1)[0]

        addr = None
        dns_start = time.time()
        resolved = False
        # Try resolving the hostname repeatedly until overall timeout
        while time.time() - dns_start < timeout:
            try:
                addr = socket.gethostbyname(host)
                logger.info("Resolved Mongo host %s -> %s", host, addr)
                resolved = True
                break
            except Exception as dns_e:
                logger.debug("DNS for %s not resolved yet: %s", host, dns_e)
             
                time.sleep(min(0.5, interval))

        if resolved:
            logger.info("Probing MongoDB at URI=%s (host=%s resolved to %s)", mongo_uri, host, addr)
        else:
            logger.info("Probing MongoDB at URI=%s (host resolution failed after retries)", mongo_uri)
    except Exception as _e:
        logger.info("Probing MongoDB at URI=%s (host resolution check skipped: %s)", mongo_uri, _e)

    while True:
        try:
            probe_client = MongoClient(
                mongo_uri,
                serverSelectionTimeoutMS=1000,
                connectTimeoutMS=1000,
            )
            probe_client.admin.command('ping')
            probe_client.close()
            logger.info("MongoDB is available")
            return True
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            # continue retrying until timeout
            elapsed = time.time() - start
            if elapsed >= timeout:
                msg = f"Timed out waiting for MongoDB after {timeout} seconds: {e}"
                logger.error(msg)
                raise TimeoutError(msg)
            logger.debug("MongoDB not ready yet: %s; retrying in %.1fs", e, interval)
            time.sleep(interval)
