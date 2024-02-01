from config.settings.base import *

SECRET_KEY = "dont-use-in-prod"

ALLOWED_HOSTS = "*"

DATABASES = {
    "default": {
        "username": "does-not-matter",
        "password": "does-not-matter",
        "dbname": "does-not-matter",
        "engine": "postgres",
        "port": 5432,
        "host": "localhost"
    }
}

AUTHBROKER_URL = "dont-use-in-prod"
