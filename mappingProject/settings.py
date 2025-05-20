from pathlib import Path
import os
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent.parent
LOG_DIR = os.path.join(BASE_DIR, 'logs')
os.makedirs(LOG_DIR, exist_ok=True)

SECRET_KEY = 'django-insecure-ykov_5&3&v40_(yvbn7nk!o-*nl#tv!m8s6%8p2!zw_)j*ba84'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'mappingUtility',
    'corsheaders',
    'rest_framework'
]

MIDDLEWARE = [
    'mappingProject.middleware.RequestIDMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware'
]

ROOT_URLCONF = 'mappingProject.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'mappingProject.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

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
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

CORS_ORIGIN_ALLOW_ALL = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

DEBUG = True

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,

    'formatters': {
        'conditional': {
            '()': 'mappingProject.custom_logging.ConditionalFormatter',
            'format': '{asctime} {levelname} {name} {message}',
            'style': '{',
        },
    },
    'filters': {
        'add_request_id': {
            '()': 'mappingProject.custom_logging.RequestIDFilter',
        },
    },

    'handlers': {
        'timed_file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': os.path.join(LOG_DIR, 'api.log'),
            # 'filename': os.path.join(LOG_DIR, f'api.{datetime.now().strftime("%Y-%m-%d")}.log'),
            'when': 'H',
            'interval': 1,
            'backupCount': 7,
            'formatter': 'conditional',
            'filters': ['add_request_id'],
        },
        'null': {
            'class': 'logging.NullHandler',
        },
    },

    'loggers': {
        'django': {
            'handlers': ['timed_file'],
            'level': 'INFO',
            'propagate': True,
        },
        'mappingUtility': {
            'handlers': ['timed_file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'django.utils.autoreload': {
            'handlers': ['null'],
            'level': 'INFO',
            'propagate': False,
        }
    }
}
