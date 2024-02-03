docker run --rm -p 6379:6379 redis:7
python manage.py runserver
celery -A aicerta worker -l info -P gevent