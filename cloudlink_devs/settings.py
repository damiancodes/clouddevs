"""
Django settings for cloudlink_devs project.
"""

from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-*m@g&%(lwkd+z1ad@xikydcsh*1*l79$ps^td4h-x4u(@!(k(c'

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

    # Your custom apps
    'services',
    'core',
    'chatbot',
    'client_portal',
    'portfolio',
    'blog',
    'quotes',
    'mpesa_api',
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

ROOT_URLCONF = 'cloudlink_devs.urls'

# Fixed templates configuration
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates'),  # Global templates
            os.path.join(BASE_DIR, 'quotes', 'templates'),  # Add quotes templates dir
        ],
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

WSGI_APPLICATION = 'cloudlink_devs.wsgi.application'
ASGI_APPLICATION = 'cloudlink_devs.asgi.application'

# Database configuration
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'cloud',
        'USER': 'root',
        'PASSWORD': '',
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'"
        }
    }
}

# Password validation
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
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static and media files configuration
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Authentication settings
LOGIN_URL = '/client/login/'

# Email settings
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
EMAIL_HOST = 'smtp.your-email-provider.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'jamhimira@gmail.com'
EMAIL_HOST_PASSWORD = ' xsvy vjls fknj keap'
DEFAULT_FROM_EMAIL = 'CloudLink_Devs <jamhimira@gmail.com>'

# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'



# Site settings
SITE_URL = 'https://www.cloudlinkdevs.com'  # Change for development as needed
ADMIN_EMAIL = 'jamhimira@gmail.com'  # For email notifications

# Payment settings
PAYPAL_CLIENT_ID = 'Ab4_efGdj3yENvZ87OVhfAOkoCx15P8G_KcnAIv4g4sWyLgyeQt0yfTWCI7ec6xJuhFOuyXVbfG2e2YZ'
CRYPTO_ADDRESS = '17EwBk4Wn6EpRg4NoxBZ2V6Ezo9dDcoA3s'
## please note this is bitcoin address with BTC Network.

# M-Pesa API Configuration
MPESA_CONFIG = {
    'CONSUMER_KEY': '2wAKKr3EQVZCjoG64vGRxk6R7vkXZapUFNYcGQsbIAaMebSD',
    'CONSUMER_SECRET': 'LVRxnPGajFSxe3EOuss7XRthQoZQKG8UBeVpbcGwgNWsbvRY1HyY5aZYjxSHZ195',
    'SHORTCODE': '174379',
    'PASS_KEY': 'bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919',
    'CALLBACK_URL': 'https://082c-102-0-17-78.ngrok-free.app/mpesa/callback/',
    'INITIATOR_NAME': 'testapi',
    'SECURITY_CREDENTIAL': 'QdAeWL42MfpZgUfWiun8XJcAEg/UH+eTDTsauWWU1TFbwxe+zclSlHMY8XzorBdkAGsQJGeEHdXuAgUokV0rzMcComvzSfqH4OgVFkNJcfdKlxs5cIylg6Q5UzeCaEqvDAJMPyZoZhvnO5gQ7zsUrTsBlksmLKek78/em1zvbb3d3CCYSPrkXSGMF9iDd8ogEH5W8sutUPzYxWL9un/SSIZpGjqjftmQwZsuXQu5naU2wPT1HZaML6g4WWxuhYD+inCn+xuLPWXB60YDm3M6E8OXM5T6cqve/zWeULnE02+3FJAI8H/FZNlIH8Q8gYuG6arBKV7aCxWq4aA66o2Bcw==',
    'TEST_MSISDN': '254795471321',
    'ACCOUNT_REFERENCE': 'CloudLink',
    'TRANSACTION_DESC': 'Payment for services',
    'ENVIRONMENT': 'sandbox',
}

# Channel layers for WebSocket (for chatbot)
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer',
    },
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'