# celery_config.py
import os
from celery import Celery
from dotenv import load_dotenv

load_dotenv()

def make_celery(app_name=__name__):
    return Celery(
        app_name,
        backend=os.getenv('CELERY_RESULT_BACKEND'),
        broker=os.getenv('CELERY_BROKER_URL')
    )

celery = make_celery()
