import os
from celery import Celery
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE','makeit.settings')
app = Celery('makeit')
app.config_from_object('django.conf:settings',namespace='CELERY')
# app.conf.update(broker_url='redis://:Aa136549.@127.0.0.1:6379/1',backend='redis://:Aa136549.@127.0.0.1:6379/1')
app.autodiscover_tasks()

