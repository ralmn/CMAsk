from celery import Celery
import settings


celery = Celery(__name__)
celery.config_from_object(settings)

@celery.task(name="name='tasks.projectid'")
def projectid(id):
    return id