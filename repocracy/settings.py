import os

DEBUG = True
TEMPLATE_DEBUG = DEBUG

BASE_PATH = os.path.dirname(__file__)

ADMINS = (
    ('Cody Soyland', 'codysoyland@gmail.com'),
    ('Chris Dickinson', 'chris@neversaw.us'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'repocracy',
        'USER': 'postgres',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}

TIME_ZONE = 'America/Chicago'
LANGUAGE_CODE = 'en-us'
SITE_ID = 1
USE_I18N = True
USE_L10N = True
MEDIA_ROOT = os.path.join(BASE_PATH, 'media')
MEDIA_URL = '/media/'
ADMIN_MEDIA_PREFIX = '/media/admin/'
SECRET_KEY = '0%m-qp$x3q3)oq99w14+3cacc2f!z#)dmns4l5&3y=12nv*^oe'

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

ROOT_URLCONF = 'repocracy.urls'

TEMPLATE_DIRS = (
    os.path.join(BASE_PATH, 'templates'),
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.admin',
    'bluebird',
    'south',
    'repo',
    'djcelery',
#    'ghettoq',
)

IS_BLUEBIRD_AUTH_PORTAL = 1
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'bluebird.backends.TwitterAuthBackend',
)
#CARROT_BACKEND = "ghettoq.taproot.Database"
CELERY_DEFAULT_EXCHANGE = "tasks"
CELERY_RESULT_BACKEND = 'database'
CELERY_RESULT_DBURI = 'postgresql://postgres@localhost/repocracy'

CELERY_IMPORTS = ('repocracy.repo.tasks',)

BROKER_HOST = "localhost"
BROKER_PORT = 5672
BROKER_VHOST = "/"
BROKER_USER = "guest"
BROKER_PASSWORD = "guest"
REPOCRACY_BASE_REPO_PATH = os.path.join(BASE_PATH, 'repos')

try:
    from local_settings import *
except ImportError:
    pass
