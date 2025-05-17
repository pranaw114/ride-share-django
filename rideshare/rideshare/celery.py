import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rideshare.settings')
app = Celery('rideshare')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
