import os
from pathlib import Path
from dotenv import load_dotenv
import dj_database_url


# ============================================================
# BASE DIRECTORY
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent


# ============================================================
# ENVIRONMENT VARIABLES
# ============================================================

load_dotenv(BASE_DIR / '.env')


# ============================================================
# SECURITY
# ============================================================

SECRET_KEY = os.getenv(
    'SECRET_KEY',
    'django-insecure-development-only-change-this'
)

DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'

ALLOWED_HOSTS = [
    host.strip()
    for host in os.getenv(
        'ALLOWED_HOSTS',
        'localhost,127.0.0.1,0.0.0.0,yusluv.org,www.yusluv.org,final-project-ioc1.onrender.com'
    ).split(',')
    if host.strip()
]

# ============================================================
# PRODUCTION SECURITY
# ============================================================

if not DEBUG:

    SECURE_SSL_REDIRECT = True

    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

    SECURE_PROXY_SSL_HEADER = (
        'HTTP_X_FORWARDED_PROTO',
        'https'
    )

else:

    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False


# ============================================================
# CSRF
# ============================================================

CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        'CSRF_TRUSTED_ORIGINS',
        'http://127.0.0.1:8000,http://localhost:8000'
    ).split(',')
    if origin.strip()
]


# ============================================================
# APPLICATION DEFINITION
# ============================================================

INSTALLED_APPS = [

    # Django
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',

    # Third-party apps
    'crispy_forms',
    'crispy_bootstrap5',

    'django_celery_results',
    'django_celery_beat',

    'rest_framework',
    'rest_framework.authtoken',

    'corsheaders',
    'django_filters',

    'import_export',
    'simple_history',
    'ckeditor',
    'phonenumber_field',

    # Cloudinary
    'cloudinary',
    'cloudinary_storage',

    # Custom application
    'travel_app',
]


# ============================================================
# MIDDLEWARE
# ============================================================

MIDDLEWARE = [

    'django.middleware.security.SecurityMiddleware',

    # Static files in production
    'whitenoise.middleware.WhiteNoiseMiddleware',

    # CORS
    'corsheaders.middleware.CorsMiddleware',

    # Django
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',

    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',

    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    # TravelBolt AI middleware
    'travel_app.middleware.AgentActivityMiddleware',
    'simple_history.middleware.HistoryRequestMiddleware',
]


# ============================================================
# URL CONFIGURATION
# ============================================================

ROOT_URLCONF = 'core.urls'


# ============================================================
# TEMPLATES
# ============================================================

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',

        'DIRS': [
            BASE_DIR / 'travel_app' / 'templates',
        ],

        'APP_DIRS': True,

        'OPTIONS': {
            'context_processors': [

                'django.template.context_processors.debug',
                'django.template.context_processors.request',

                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',

                # TravelBolt AI context processors
                'travel_app.context_processors.agent_context',
                'travel_app.context_processors.notification_context',
                'travel_app.context_processors.system_context',
            ],
        },
    },
]


# ============================================================
# WSGI
# ============================================================

WSGI_APPLICATION = 'core.wsgi.application'


# ============================================================
# DATABASE
# ============================================================

DATABASES = {
    'default': dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=600,
    )
}

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }


# ============================================================
# PASSWORD VALIDATION
# ============================================================

AUTH_PASSWORD_VALIDATORS = [

    {
        'NAME':
        'django.contrib.auth.password_validation.'
        'UserAttributeSimilarityValidator',
    },

    {
        'NAME':
        'django.contrib.auth.password_validation.'
        'MinimumLengthValidator',
    },

    {
        'NAME':
        'django.contrib.auth.password_validation.'
        'CommonPasswordValidator',
    },

    {
        'NAME':
        'django.contrib.auth.password_validation.'
        'NumericPasswordValidator',
    },
]


# ============================================================
# INTERNATIONALIZATION
# ============================================================

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Riyadh'

USE_I18N = True

USE_TZ = True


# ============================================================
# STATIC FILES
# ============================================================

STATIC_URL = '/static/'

STATIC_ROOT = BASE_DIR / 'staticfiles'

STATICFILES_DIRS = [
    BASE_DIR / 'static',
    BASE_DIR / 'travel_app' / 'static',
]

STATICFILES_STORAGE = (
    'whitenoise.storage.CompressedManifestStaticFilesStorage'
)


# ============================================================
# MEDIA FILES
# ============================================================

CLOUDINARY_STORAGE = {
    'CLOUD_NAME': os.getenv('CLOUDINARY_CLOUD_NAME'),
    'API_KEY': os.getenv('CLOUDINARY_API_KEY'),
    'API_SECRET': os.getenv('CLOUDINARY_API_SECRET'),
}

DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

# MEDIA_URL = '/media/'

# MEDIA_ROOT = BASE_DIR / 'media'


# ============================================================
# DEFAULT PRIMARY KEY
# ============================================================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ============================================================
# CUSTOM USER MODEL
# ============================================================

AUTH_USER_MODEL = 'travel_app.Agent'


# ============================================================
# CRISPY FORMS
# ============================================================

CRISPY_ALLOWED_TEMPLATE_PACKS = 'bootstrap5'

CRISPY_TEMPLATE_PACK = 'bootstrap5'


# ============================================================
# LOGIN / LOGOUT
# ============================================================

LOGIN_URL = '/client/login/'

LOGIN_REDIRECT_URL = '/client/dashboard/'

LOGOUT_REDIRECT_URL = '/client/login/'


# ============================================================
# EMAIL CONFIGURATION
# ============================================================

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

EMAIL_HOST = os.getenv(
    'EMAIL_HOST',
    'smtp.gmail.com'
)

EMAIL_PORT = int(
    os.getenv(
        'EMAIL_PORT',
        '587'
    )
)

EMAIL_USE_TLS = True

EMAIL_USE_SSL = False

EMAIL_HOST_USER = os.getenv(
    'EMAIL_HOST_USER'
)

EMAIL_HOST_PASSWORD = os.getenv(
    'EMAIL_HOST_PASSWORD'
)

DEFAULT_FROM_EMAIL = os.getenv(
    'DEFAULT_FROM_EMAIL',
    'Travelbolt_AI <yusufakinbodeajayi@gmail.com>'
)


# ============================================================
# CELERY
# ============================================================

CELERY_BROKER_URL = os.getenv(
    'CELERY_BROKER_URL',
    'redis://localhost:6379/0'
)

CELERY_RESULT_BACKEND = 'django-db'

CELERY_ACCEPT_CONTENT = [
    'application/json'
]

CELERY_TASK_SERIALIZER = 'json'

CELERY_RESULT_SERIALIZER = 'json'

CELERY_TIMEZONE = TIME_ZONE

CELERY_BEAT_SCHEDULER = (
    'django_celery_beat.schedulers:DatabaseScheduler'
)


# ============================================================
# REDIS CACHE
# ============================================================

CACHES = {

    'default': {

        'BACKEND':
        'django.core.cache.backends.redis.RedisCache',

        'LOCATION': os.getenv(
            'REDIS_URL',
            'redis://localhost:6379/1'
        ),
    }
}


# ============================================================
# DJANGO REST FRAMEWORK
# ============================================================

REST_FRAMEWORK = {

    'DEFAULT_AUTHENTICATION_CLASSES': [

        'rest_framework.authentication.'
        'SessionAuthentication',

        'rest_framework.authentication.'
        'TokenAuthentication',
    ],

    'DEFAULT_PERMISSION_CLASSES': [

        'rest_framework.permissions.'
        'IsAuthenticated',
    ],

    'DEFAULT_FILTER_BACKENDS': [

        'django_filters.rest_framework.'
        'DjangoFilterBackend',

        'rest_framework.filters.SearchFilter',

        'rest_framework.filters.OrderingFilter',
    ],

    'DEFAULT_PAGINATION_CLASS':
        'rest_framework.pagination.PageNumberPagination',

    'PAGE_SIZE': 20,
}


# ============================================================
# CORS
# ============================================================

CORS_ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        'CORS_ALLOWED_ORIGINS',
        'http://localhost:8000'
    ).split(',')
    if origin.strip()
]

CORS_ALLOW_CREDENTIALS = True


# ============================================================
# LOGGING
# ============================================================
# IMPORTANT:
# Render captures console logs automatically.
# Do NOT use logging.FileHandler here because the logs/
# directory may not exist on Render.
# ============================================================

LOGGING = {

    'version': 1,

    'disable_existing_loggers': False,

    'formatters': {

        'verbose': {

            'format':
                '{levelname} {asctime} {module} '
                '{process:d} {thread:d} {message}',

            'style': '{',
        },

        'simple': {

            'format':
                '{levelname} {asctime} {message}',

            'style': '{',
        },
    },

    'handlers': {

        'console': {

            'level': 'INFO',

            'class':
                'logging.StreamHandler',

            'formatter':
                'simple',
        },
    },

    'loggers': {

        'django': {

            'handlers': [
                'console'
            ],

            'level':
                'INFO',

            'propagate':
                False,
        },

        'travel_app': {

            'handlers': [
                'console'
            ],

            'level':
                'INFO',

            'propagate':
                False,
        },
    },
}


# ============================================================
# WHATSAPP BUSINESS API
# ============================================================

WHATSAPP_API_KEY = os.getenv(
    'WHATSAPP_API_KEY'
)

WHATSAPP_PHONE_NUMBER_ID = os.getenv(
    'WHATSAPP_PHONE_NUMBER_ID'
)

WHATSAPP_BUSINESS_ACCOUNT_ID = os.getenv(
    'WHATSAPP_BUSINESS_ACCOUNT_ID'
)


# ============================================================
# TWILIO
# ============================================================

TWILIO_ACCOUNT_SID = os.getenv(
    'TWILIO_ACCOUNT_SID'
)

TWILIO_AUTH_TOKEN = os.getenv(
    'TWILIO_AUTH_TOKEN'
)

TWILIO_WHATSAPP_NUMBER = os.getenv(
    'TWILIO_WHATSAPP_NUMBER'
)


# ============================================================
# LETSFG
# ============================================================

LETSFG_API_KEY = os.getenv(
    'LETSFG_API_KEY'
)


# ============================================================
# AMADEUS
# ============================================================

AMADEUS_API_KEY = os.getenv(
    'AMADEUS_API_KEY'
)

AMADEUS_API_SECRET = os.getenv(
    'AMADEUS_API_SECRET'
)


# ============================================================
# OPENAI
# ============================================================

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
# ============================================================
# PAYSTACK
# ============================================================

PAYSTACK_PUBLIC_KEY = os.getenv(
    'PAYSTACK_PUBLIC_KEY'
)

PAYSTACK_SECRET_KEY = os.getenv(
    'PAYSTACK_SECRET_KEY'
)


# ============================================================
# FILE UPLOAD SETTINGS
# ============================================================

FILE_UPLOAD_MAX_MEMORY_SIZE = (
    10 * 1024 * 1024
)

DATA_UPLOAD_MAX_MEMORY_SIZE = (
    10 * 1024 * 1024
)
