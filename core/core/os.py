from .settings  import *

DEBUG = False

ALLOWED_HOSTS = ["IP","dominio.com","www.dominio.com"]

CSRF_TRUSTED_ORIGINS = ['https://dominio.com','https://www.dominio.com']

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': '/home/aieco/logs/django.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
}