from celery import Celery

from backend.app.config import get_settings
from backend.app.db import Repository
from backend.app.services.runs import execute_run

settings = get_settings()
celery_app = Celery("defi_stress", broker=settings.redis_url, backend=settings.redis_url)
celery_app.conf.task_track_started = True
celery_app.conf.task_serializer = "json"
celery_app.conf.result_serializer = "json"


@celery_app.task(name="defi_stress.execute_run")
def execute_run_task(run_id: str, mode: str) -> dict:
    repository = Repository(settings.database_url)
    return execute_run(repository, run_id, mode)
