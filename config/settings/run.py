import dj_database_url
from dbt_copilot_python.database import database_url_from_env

from config.settings.base import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = (os.getenv('SECRET_KEY'))

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS')

# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    "default": dj_database_url.config(
        default=database_url_from_env("DATABASE_CREDENTIALS")
    )
}

AUTHBROKER_URL = os.getenv("AUTHBROKER_URL")
AUTHBROKER_CLIENT_ID = os.getenv("AUTHBROKER_CLIENT_ID")
AUTHBROKER_CLIENT_SECRET = os.getenv("AUTHBROKER_CLIENT_SECRET")
AUTHBROKER_SCOPES = "read write"
RESTRICT_ADMIN = env.bool("RESTRICT_ADMIN", True)

CF_USERNAME = os.getenv("CF_USERNAME")
CF_PASSWORD = os.getenv("CF_PASSWORD")
CF_DOMAIN = os.getenv("CF_DOMAIN")
ORG_GUID = os.getenv("ORG_GUID")
BIND_ENABLED = os.getenv("BIND_ENABLED")
SLACK_ENABLED = os.getenv("SLACK_ENABLED")
SLACK_TOKEN = os.getenv("SLACK_TOKEN")
SLACK_URL = os.getenv("SLACK_URL")
SLACK_CHANNEL = os.getenv("SLACK_CHANNEL")
