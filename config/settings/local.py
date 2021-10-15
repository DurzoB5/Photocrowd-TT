from .base import *  # noqa
from .base import env

# GENERAL
# ------------------------------------------------------------------------------
DEBUG = True
ALLOWED_HOSTS = ['*']

# CACHES
# ------------------------------------------------------------------------------
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': '',
    }
}

# EMAIL
# ------------------------------------------------------------------------------
EMAIL_BACKEND = env(
    'DJANGO_EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend'
)

# WHITENOISE
# ------------------------------------------------------------------------------
INSTALLED_APPS = ['whitenoise.runserver_nostatic'] + INSTALLED_APPS  # noqa F405

# DJANGO_DEBUG_TOOLBAR
# ------------------------------------------------------------------------------
INSTALLED_APPS += ['debug_toolbar']  # noqa F405
MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']  # noqa F405
DEBUG_TOOLBAR_CONFIG = {
    'DISABLE_PANELS': ['debug_toolbar.panels.redirects.RedirectsPanel'],
    'SHOW_TEMPLATE_CONTEXT': True,
}
INTERNAL_IPS = ['127.0.0.1', '10.0.2.2']

# DJANGO_EXTENSIONS
# ------------------------------------------------------------------------------
INSTALLED_APPS += ['django_extensions']  # noqa F405

# DJANGO CORS
# -------------------------------------------------------------------------------
CORS_ALLOWED_ORIGINS = env.list(
    'CORS_ALLOWED_ORIGINS',
    default=['http://localhost:3000', 'http://0.0.0.0:3000', 'http://127.0.0.1:3000'],
)
CORS_ALLOW_CREDENTIALS = env.bool('CORS_ALLOW_CREDENTIALS', default=True)
CORS_EXPOSE_HEADERS = env.list(
    'CORS_EXPOSE_HEADERS',
    default=[],
)

# COOKIE
# -------------------------------------------------------------------------------
SESSION_COOKIE_DOMAIN = env('SESSION_COOKIE_DOMAIN', default=None)
SESSION_COOKIE_SAMESITE = env('SESSION_COOKIE_SAMESITE', default='Lax')
CSRF_COOKIE_DOMAIN = env('CSRF_COOKIE_DOMAIN', default=None)
