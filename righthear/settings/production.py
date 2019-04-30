from .base import *

DEBUG = False

MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware', ]
ALLOWED_HOSTS=['35.196.96.207:8000',]