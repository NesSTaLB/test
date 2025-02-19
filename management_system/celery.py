from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'management_system.settings')

app = Celery('management_system')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# المهام المجدولة
app.conf.beat_schedule = {
    'check-low-stock-daily': {
        'task': 'sales.tasks.check_low_stock',
        'schedule': crontab(hour=9, minute=0),  # كل يوم الساعة 9 صباحاً
    },
    'send-daily-task-reminders': {
        'task': 'project_management.tasks.send_task_reminders',
        'schedule': crontab(hour=8, minute=0),  # كل يوم الساعة 8 صباحاً
    },
    'update-sales-statistics': {
        'task': 'sales.tasks.update_sales_statistics',
        'schedule': crontab(minute=0, hour='*/1'),  # كل ساعة
    },
    'generate-daily-reports': {
        'task': 'dashboard.tasks.generate_daily_reports',
        'schedule': crontab(hour=23, minute=45),  # كل يوم الساعة 11:45 مساءً
    },
    'check-overdue-tasks': {
        'task': 'project_management.tasks.check_overdue_tasks',
        'schedule': crontab(hour='*/2', minute=0),  # كل ساعتين
    },
    'sync-inventory': {
        'task': 'sales.tasks.sync_inventory',
        'schedule': crontab(minute=0, hour='*/4'),  # كل 4 ساعات
    },
    'backup-database': {
        'task': 'management_system.tasks.backup_database',
        'schedule': crontab(hour=2, minute=0),  # كل يوم الساعة 2 صباحاً
    }
}

@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')