LOCAL SERVER:
docker run --rm -p 6379:6379 redis:7
python manage.py runserver
celery -A aicerta worker -l info -P gevent

ON DIGITAL OCEAN:
daphne -b 0.0.0.0 -p 8080 aicerta.asgi:application
celery -A aicerta worker -l info
REDIS:
