from pathlib import Path
import os
from pathlib import Path
from datetime import timedelta

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# SECRET_KEY = 'django-insecure-xt_ce-7#nn%a3)69wm1#i4^-1-119iz_5&sw+an9t2xtbe49)8'

# SECURITY WARNING: don't run with debug turned on in production!
# DEBUG = True

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'storages',

    'users.apps.UsersConfig',
    'posts.apps.PostsConfig',
    'interactions.apps.InteractionsConfig',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

CORS_ALLOW_ALL_ORIGINS = True

CORS_ALLOW_CREDENTIALS = True

ROOT_URLCONF = 'core.urls'

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

WSGI_APPLICATION = 'core.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': os.environ.get('DB_ENGINE', 'django.db.backends.postgresql'),
        'NAME': os.environ.get('DB_NAME', 'postgres_db'),
        'USER': os.environ.get('DB_USER', 'postgres'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'pass'),
        'HOST': os.environ.get('DB_HOST', 'db'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}

SECRET_KEY = os.environ.get('SECRET_KEY', 'your-default-secret-key-if-env-var-is-not-set')
DEBUG = os.environ.get('DEBUG', 'True') == 'True'

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


LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Almaty'

USE_I18N = True

USE_TZ = True

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
            'propagate': False,
        },
        # --- Добавляем логгеры для AWS ---
        'boto3': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'botocore': {
            'handlers': ['console'],
            'level': 'DEBUG', 
            'propagate': True,
        },
        'storages': {
            'handlers': ['console'],
            'level': 'DEBUG', 
            'propagate': True,
        }
    }
}


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = 'static/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": True,
}

# --- Настройки для работы с AWS S3 ---
STORAGES = {
    "default": {
        "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
        "OPTIONS": {
            "access_key": os.environ.get('AWS_ACCESS_KEY_ID'),
            "secret_key": os.environ.get('AWS_SECRET_ACCESS_KEY'),
            "bucket_name": os.environ.get('AWS_STORAGE_BUCKET_NAME'),
            "region_name": os.environ.get('AWS_S3_REGION_NAME', 'eu-north-1'),

            "default_acl": os.environ.get('AWS_DEFAULT_ACL', 'private'),
            "location": os.environ.get('AWS_LOCATION', 'media'),
            "file_overwrite": False,
            "object_parameters": {
                'CacheControl': 'max-age=86400',
            },
            "signature_version": 's3v4',
            # "addressing_style": 'virtual',
            # "endpoint_url": f'https://s3.{os.environ.get("AWS_S3_REGION_NAME", "eu-north-1")}.amazonaws.com',
            "custom_domain": f'{os.environ.get("AWS_STORAGE_BUCKET_NAME")}.s3.{os.environ.get("AWS_S3_REGION_NAME", "eu-north-1")}.amazonaws.com',
        },
    },
    "staticfiles": {
         "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
         # Для S3:
         # "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
         # "OPTIONS": {
         #     # ... настройки AWS для статики ...
         #     "location": "static", # Обычно отдельная папка для статики
         #     "default_acl": "public-read", # Статика должна быть публичной
         # },
    },
}

# AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
# AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')

# # Название S3 бакета (читаем из переменной окружения)
# AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')

# # Имя региона бакета (читаем из переменной окружения)
# AWS_S3_REGION_NAME = os.environ.get('AWS_S3_REGION_NAME', 'eu-north-1')

# # Указываем Django использовать S3 для хранения медиафайлов по умолчанию
# DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

# # --- Опциональные, но полезные настройки ---

# # 'public-read' - файлы будут доступны для чтения по прямой ссылке
# AWS_DEFAULT_ACL = os.environ.get('AWS_DEFAULT_ACL', 'public-read') # Начнем с public-read для простоты

# # Поддиректория внутри бакета для медиафайлов (опционально)
# AWS_LOCATION = os.environ.get('AWS_LOCATION', 'media')

# MEDIA_URL = f'https://{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/{AWS_LOCATION}/'

# # Не перезаписывать файлы с одинаковыми именами (генерировать уникальные)
# AWS_S3_FILE_OVERWRITE = False

# # Контроль кеширования (опционально)
# AWS_S3_OBJECT_PARAMETERS = {
#     'CacheControl': 'max-age=86400', # Кешировать на 1 день
# }

# AWS_S3_SIGNATURE_VERSION = 's3v4' # Рекомендуется