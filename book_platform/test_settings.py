# Test Configuration for Book Platform
# This file contains settings optimized for testing

import os
from .settings import *

# Use in-memory SQLite database for faster tests
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
        'OPTIONS': {
            'timeout': 20,
        }
    }
}

# Disable migrations during tests for speed
class DisableMigrations:
    def __contains__(self, item):
        return True
    
    def __getitem__(self, item):
        return None

MIGRATION_MODULES = DisableMigrations()

# Use simpler password hashing for tests
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Disable logging during tests
LOGGING_CONFIG = None
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'null': {
            'class': 'logging.NullHandler',
        },
    },
    'root': {
        'handlers': ['null'],
    },
}

# Use temporary directory for media files during tests
import tempfile
MEDIA_ROOT = tempfile.mkdtemp()

# Disable cache during tests
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# Email backend for testing
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# Disable CSRF during tests
CSRF_COOKIE_SECURE = False
CSRF_USE_SESSIONS = False

# Test-specific settings
TEST_RUNNER = 'django.test.runner.DiscoverRunner'

# Set DEBUG to False for production-like testing
DEBUG = False

# Simple secret key for tests
SECRET_KEY = 'test-secret-key-for-testing-only'

# Allowed hosts for testing
ALLOWED_HOSTS = ['testserver', 'localhost', '127.0.0.1']

# Disable static file compression during tests
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# Simplified middleware for tests
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Test file upload settings
FILE_UPLOAD_MAX_MEMORY_SIZE = 1024 * 1024 * 5  # 5MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 1024 * 1024 * 10  # 10MB

# Test-specific CKEditor settings
CKEDITOR_5_CONFIGS = {
    'extends': {
        'toolbar': ['heading', '|', 'bold', 'italic'],
        'height': '200px',
        'width': '100%',
    }
}

# Disable auto-discovery of tests in migrations
TEST_DISCOVER_TOP_LEVEL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEST_DISCOVER_PATTERN = "test_*.py"

# Test coverage settings
COVERAGE_MODULE_EXCLUDES = [
    'tests$', 'settings$', 'urls$', 'locale$',
    'migrations', 'fixtures', 'venv', 'virtualenv',
    '__pycache__'
]

# Selenium settings for integration tests
USE_SELENIUM = os.environ.get('USE_SELENIUM', False)

if USE_SELENIUM:
    from selenium import webdriver
    SELENIUM_WEBDRIVER = webdriver.Chrome  # or webdriver.Firefox
    SELENIUM_HEADLESS = True

# Rest Framework settings for API tests
REST_FRAMEWORK.update({
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
    'TEST_REQUEST_DEFAULT_FORMAT': 'json',
})

print("Using test settings configuration")
