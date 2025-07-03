import os
import dj_database_url
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-bd!q_oz_0pu)h#x&f=bhb@@d+1$1d&2=h83&m2s##9%2r*re#&'

# SECURITY WARNING: don't run with debug turned on in production!


DEBUG = True # Esto es una buena práctica para controlar DEBUG

ALLOWED_HOSTS = ['127.0.0.1', 'localhost', 'anfavillarrica-production.up.railway.app']
CSRF_TRUSTED_ORIGINS = [
    'http://127.0.0.1',
    'http://localhost',
    'https://anfavillarrica-production.up.railway.app'
]


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'app_login',
    'app_main',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
]

ROOT_URLCONF = 'project_anfa.urls'

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

WSGI_APPLICATION = 'project_anfa.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

# --- ¡¡CAMBIO CLAVE AQUÍ!! ---
DATABASES = {
    'default': dj_database_url.config(
        # Por defecto, dj_database_url busca la variable de entorno DATABASE_URL.
        # Si no la encuentra, usa el 'default' que le pases.
        # Aquí, queremos que use la PUBLIC_DATABASE_URL que Railway CLI inyectará
        # cuando ejecutes 'railway run', o la DATABASE_URL interna de Railway.
        # Si ninguna está presente (para desarrollo local sin DB externa), usa SQLite.
        default=os.environ.get('PUBLIC_DATABASE_URL') or \
                os.environ.get('DATABASE_URL') or \
                f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=600,
        ssl_require=True # Esto es para PostgreSQL. Asegúrate de que tu SQLite no lo necesite.
                         # Normalmente no es necesario para SQLite, pero no causará daño.
                         # Si te da problemas, puedes envolverlo en un if/else para SSL en prod.
    )
}

# -----------------------------


# Password validation
# https://docs.djangoproject.com/en/5.1/topics/i18n/

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
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# WhiteNoise para servir archivos estáticos en producción
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Ya lo tienes arriba. Elimina esta duplicación si está.
# STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage' 
# DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'