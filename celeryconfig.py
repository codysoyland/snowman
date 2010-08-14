CARROT_BACKEND = "ghettoq.taproot.Database"
CELERY_DEFAULT_EXCHANGE = "tasks"
CELERY_RESULT_BACKEND = 'database'
CELERY_RESULT_DBURI = 'postgresql://postgres@localhost/repocracy'

CELERY_IMPORTS = ('repo.tasks',)

BROKER_HOST = "localhost"
BROKER_PORT = 5672
BROKER_VHOST = "/"
BROKER_USER = "guest"
BROKER_PASSWORD = "guest"
