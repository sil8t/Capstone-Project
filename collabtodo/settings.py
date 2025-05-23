"""
Django settings for the CollabToDo project.

Generated by 'django-admin startproject' using Django 5.1.7.

Docs:
- General settings: https://docs.djangoproject.com/en/5.1/topics/settings/
- Full config reference: https://docs.djangoproject.com/en/5.1/ref/settings/
"""

import os
from pathlib import Path

# Base directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent

# ─────────────────────────────────────────────
# SECURITY
# ─────────────────────────────────────────────

SECRET_KEY = 'django-insecure-ko=6c5grulbcfextuj+&uu%q^0e=cvxxgi(7#*5#1#uvxr39vc'  # Replace in production
DEBUG = True
ALLOWED_HOSTS = []

# ─────────────────────────────────────────────
# APPLICATIONS
# ─────────────────────────────────────────────

INSTALLED_APPS = [
    # Django built-in apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Project apps
    'tasks',

    # Third-party apps
    'channels',
    'tailwind',
    'theme',
    'django_browser_reload',
]

# ─────────────────────────────────────────────
# MIDDLEWARE
# ─────────────────────────────────────────────

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_browser_reload.middleware.BrowserReloadMiddleware',
]

# ─────────────────────────────────────────────
# TEMPLATES
# ─────────────────────────────────────────────

ROOT_URLCONF = 'collabtodo.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],  # Add template paths here if needed
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

# ─────────────────────────────────────────────
# ASGI / CHANNELS
# ─────────────────────────────────────────────

ASGI_APPLICATION = 'collabtodo.asgi.application'
WSGI_APPLICATION = 'collabtodo.wsgi.application'

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer',
    },
}

# ─────────────────────────────────────────────
# DATABASE
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases
# ─────────────────────────────────────────────

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# ─────────────────────────────────────────────
# PASSWORD VALIDATION
# ─────────────────────────────────────────────

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ─────────────────────────────────────────────
# LOCALIZATION
# ─────────────────────────────────────────────

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# ─────────────────────────────────────────────
# STATIC FILES
# https://docs.djangoproject.com/en/5.1/howto/static-files/
# ─────────────────────────────────────────────

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / "tasks" / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

# ─────────────────────────────────────────────
# DEFAULT PRIMARY KEY FIELD
# ─────────────────────────────────────────────

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ─────────────────────────────────────────────
# AUTH SETTINGS
# ─────────────────────────────────────────────

LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/tasks/'
LOGOUT_REDIRECT_URL = '/accounts/login/'

# ─────────────────────────────────────────────
# TAILWIND CONFIGURATION
# ─────────────────────────────────────────────

TAILWIND_APP_NAME = 'theme'
