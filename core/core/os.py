from .settings  import *

NPM_BIN_PATH = '/usr/bin/npm'

DEBUG = False

ALLOWED_HOSTS = ["5.183.9.247","aieco.com.co","www.aieco.com.co"]

CSRF_TRUSTED_ORIGINS = ['https://aieco.com.co','https://www.aieco.com.co']

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': '/home/app/aieco/core/logs/django.log',
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
