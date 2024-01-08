web: python manage.py migrate && gunicorn -b 0.0.0.0:$PORT config.wsgi:application
hourlycheck: python manage.py daily_check
