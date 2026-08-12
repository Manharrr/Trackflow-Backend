import os

from celery.schedules import crontab

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("config")

app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

# Beat schedules
app.conf.beat_schedule = {
    "cleanup-expired-activations-daily": {
        "task": "apps.employees.task.cleanup_expired_activations",
        "schedule": crontab(hour=1, minute=0),  # daily 1:00 AM
    },
}

from datetime import timedelta

app.conf.beat_schedule = {
    "cleanup-every-minute": {
        "task": "apps.employees.task.cleanup_expired_activations",
        "schedule": timedelta(minutes=1),
    },
}

# Autodiscover tasks in both tasks.py and task.py patterns
app.autodiscover_tasks(related_name='tasks')
app.autodiscover_tasks(related_name='task')

app.conf.beat_schedule = {
    "daily-operations-summary": {
        "task": "apps.analytics.tasks.send_daily_operations_summary",
        "schedule": crontab(hour=8, minute=0),  # Daily 8:00 AM
    },
}

# app.conf.beat_schedule = {
#     "daily-operations-summary": {
#         "task": "apps.analytics.tasks.send_daily_operations_summary",
#         "schedule": timedelta(minutes=1),
#     },
# }