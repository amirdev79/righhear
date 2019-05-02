"""
Django settings for righthear project.

Generated by 'django-admin startproject' using Django 2.1.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_DB_DIR = '/var/lib/postgresql/10/main'
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # .../righthear

BASE_STORAGE_PATH = '/rhdata'

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_STORAGE_PATH, 'media')

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_STORAGE_PATH, 'static')

STATICFILES_DIRS = (PROJECT_DIR + '/static',)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ['SECRET_KEY']


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'users',
    'events',
    'utils',
    'adminsortable',
    'django.contrib.gis'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'righthear.urls'

AUTHENTICATION_BACKENDS = ['utils.network.PasswordlessAuthBackend', 'django.contrib.auth.backends.ModelBackend']

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'righthear.wsgi.application'

# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        # 'ENGINE': 'django.db.backends.postgresql',
        # 'NAME': os.path.join(BASE_DB_DIR, 'rhdb'),
        'NAME': 'rhdb',
        'USER': 'postgres',
        'PASSWORD': '6429005',
        'HOST': 'localhost',
        'PORT': 5432,

    }
}

# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Jerusalem'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/

STATIC_URL = '/static/'

GOOGLE_API_KEY = 'AIzaSyCcESmpfQinXSNCbVVnIbAVq3MWbcs_v_o'

EASY_CO_IL_USERNAME = 'easy_scraper'
TLV_SCRAPER_USERNAME = 'tlv_scraper'

EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'righthearil@gmail.com'
EMAIL_HOST_PASSWORD = 'Z12xc34V'
EMAIL_PORT = 587

DEFAULT_EMAIL = 'righthearil@gmail.com'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'root': {
                'level': 'DEBUG',
                'handlers': ['console'],
            },
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'gunicorn': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'verbose',
            'filename': 'logs/gunicorn.log',
            'maxBytes': 1024 * 1024 * 100,  # 100 mb
        },
        'django_error': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'verbose',
            'filename': 'logs/django_error.log',
            'maxBytes': 1024 * 1024 * 100,  # 100 mb
        },
        'django_access': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'simple',
            'filename': 'logs/django_access.log',
            'maxBytes': 1024 * 1024 * 100,  # 100 mb
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        }
    },
    'loggers': {
        'django': {
            'handlers': ['django_access'],
            'propagate': True,
        },
        'django.request': {
            'level': 'ERROR',
            'handlers': ['console','django_error'],
            'propagate': False,
        },
        'gunicorn.errors': {
            'level': 'DEBUG',
            'handlers': ['gunicorn'],
            'propagate': False,
        },
    },
}

ADMINS = [('Amir', 'amirdev79Gmail.com')]