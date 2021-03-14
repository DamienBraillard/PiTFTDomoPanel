import sys

# GPIO configuration
PIN_PIR = 4
PIN_BACKLIGHT = 18
MOCK_PINS = True

# Screen configuration
SCREEN_TIMEOUT = 30
SCREEN_DISPLAY = ":0"

# Home automation box configuration
HOME_AUTOMATION_BOX_URL = "http://10.10.10.29/script/?exec=info_display.php"

# User interface
LOCALE = "fr_CH.utf8"

# Logging
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': "[%(levelname)4.4s %(asctime)s %(module)s:%(lineno)d] %(message)s",
            'datefmt': "%Y-%m-%d+%H:%M:%S",
        },
    },
    'handlers': {
        'default': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
            'stream': sys.stdout,
        },
        'rotating_to_file': {
            'level': 'DEBUG',
            'class': "logging.handlers.RotatingFileHandler",
            'formatter': 'standard',
            "filename": "app.log",
            "maxBytes": 10000,
            "backupCount": 10,
        },
    },
    'loggers': {
        '': {
            'handlers': ['default', 'rotating_to_file'],
            'level': 'DEBUG',
            'propagate': True
        }
    }
}
