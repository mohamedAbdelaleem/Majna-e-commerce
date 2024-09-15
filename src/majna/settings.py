"""
Django settings for majna project.

Generated by 'django-admin startproject' using Django 4.2.6.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

import os
from pathlib import Path
import local_settings

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = local_settings.SECRET_KEY

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "knox",
    "storages",
    "accounts",
    "brands",
    "brands_applications",
    "addresses",
    "products",
    "carts",
    "orders",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "majna.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "majna.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = local_settings.DATABASES_CONF


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {
            "min_length": 6,
        },
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = "static/"

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Authentication

AUTH_USER_MODEL = "accounts.CustomUser"
REQUIRE_ACCOUNT_ACTIVATION = True
FRONTEND_BASE_URL = "http://localhost:3000/"

# Rest Framework

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": ("knox.auth.TokenAuthentication",),
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
    ],
    "DEFAULT_PARSER_CLASSES": [
        "rest_framework.parsers.JSONParser",
        "rest_framework.parsers.MultiPartParser",
        "rest_framework.parsers.FormParser",
    ],
    "EXCEPTION_HANDLER": "utils.exception_handler.custom_exception_handler",
}

REST_KNOX = local_settings.REST_KNOX

# Email
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_USE_TLS = True
EMAIL_PORT = 587
EMAIL_HOST_USER = local_settings.EMAIL_HOST_USER
EMAIL_HOST_PASSWORD = local_settings.EMAIL_HOST_PASSWORD

DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# Media
MEDIA_ROOT = os.path.join(BASE_DIR, "media")
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024
SUPABASE_URL = local_settings.SUPABASE_URL
SUPABASE_KEY = local_settings.SERVICE_KEY


## S3
AWS_ACCESS_KEY_ID = os.environ.get(
    "AWS_ACCESS_KEY_ID", default=local_settings.AWS_ACCESS_KEY_ID
)
AWS_SECRET_ACCESS_KEY = os.environ.get(
    "AWS_SECRET_ACCESS_KEY", default=local_settings.AWS_SECRET_ACCESS_KEY
)
AWS_STORAGE_BUCKET_NAME = os.environ.get(
    "AWS_STORAGE_BUCKET_NAME", default=local_settings.AWS_STORAGE_BUCKET_NAME
)
AWS_S3_CUSTOM_DOMAIN = f"{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com"


# STORAGES = {
#     # Media Files
#     "default": {
#         "BACKEND": "storages.backends.s3.S3Storage",
#     },
#     "staticfiles": {"BACKEND": "storages.backends.s3.S3Storage"},
# }


STRIPE_SECRET = os.environ.get(
    "STRIPE_SECRET", default=local_settings.STRIPE_SECRET
)
STRIPE_PUBLISHER = os.environ.get(
    "STRIPE_PUBLISHER", default=local_settings.STRIPE_PUBLISHER
)
STRIPE_ENDPOINT_SECRET = os.environ.get(
    "STRIPE_ENDPOINT_SECRET", default=local_settings.STRIPE_ENDPOINT_SECRET
)
