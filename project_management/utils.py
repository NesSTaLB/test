from django.db.models import Q, Count
from datetime import datetime, timedelta
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from .models import Task

def calculate_project_progress(project):
    """
    حساب نسبة تقدم المشروع بناءً على المهام المكتملة
    """
    total_tasks = project.tasks.count()
    if total_tasks == 0:
        return 0
        
    completed_tasks = project.tasks.filter(status='completed').count()
    return (completed_tasks / total_tasks) * 100

def get_overdue_tasks(user=None):
    """
    الحصول على المهام المتأخرة
    """
    today = timezone.now().date()
    query = Q(due_date__lt=today) & Q(status__in=['todo', 'in_progress', 'review'])
    
    if user:
        query &= Q(assigned_to=user)
        
    return Task.objects.filter(query)

def notify_task_assignment(task):
    """
    إرسال إشعار عند إسناد مهمة جديدة
    """
    if task.assigned_to and task.assigned_to.email:
        subject = f'تم إسناد مهمة جديدة: {task.title}'
        message = f"""
        مرحباً {task.assigned_to.get_full_name()},
        
        تم إسناد مهمة جديدة إليك:
        
        العنوان: {task.title}
        المشروع: {task.project.name}
        تاريخ الاستحقاق: {task.due_date}
        الأولوية: {task.get_priority_display()}
        
        يمكنك عرض تفاصيل المهمة من خلال لوحة التحكم.
        """
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [task.assigned_to.email],
        )

def notify_upcoming_deadlines():
    """
    إرسال إشعارات للمهام التي يقترب موعد تسليمها
    """
    tomorrow = datetime.now().date() + timedelta(days=1)
    upcoming_tasks = Task.objects.filter(
        due_date=tomorrow,
        status__in=['todo', 'in_progress']
    ).select_related('assigned_to', 'project')

    for task in upcoming_tasks:
        if task.assigned_to and task.assigned_to.email:
            subject = f'تذكير: موعد تسليم المهمة غداً - {task.title}'
            message = f"""
            مرحباً {task.assigned_to.get_full_name()},
            
            تذكير: يجب تسليم المهمة التالية غداً:
            
            العنوان: {task.title}
            المشروع: {task.project.name}
            الحالة: {task.get_status_display()}
            
            يرجى إكمال المهمة في الوقت المحدد.
            """
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [task.assigned_to.email],
            )

def calculate_team_workload(team_members):
    """
    حساب عبء العمل لأعضاء الفريق
    """
    workload = {}
    
    for member in team_members:
        assigned_tasks = Task.objects.filter(
            assigned_to=member,
            status__in=['todo', 'in_progress', 'review']
        )
        total_estimated_hours = sum(
            task.estimated_hours for task in assigned_tasks if task.estimated_hours
        )
        workload[member.username] = {
            'total_tasks': assigned_tasks.count(),
            'estimated_hours': total_estimated_hours,
            'high_priority_tasks': assigned_tasks.filter(priority='high').count()
        }
    
    return workload

def calculate_workload(user):
    """
    حساب عبء العمل للمستخدم
    """
    today = timezone.now().date()
    active_tasks = user.assigned_tasks.filter(
        status__in=['todo', 'in_progress', 'review'],
        due_date__gte=today
    )
    
    total_estimated_hours = sum(
        task.estimated_hours or 0 
        for task in active_tasks
    )
    
    return {
        'active_tasks_count': active_tasks.count(),
        'total_estimated_hours': total_estimated_hours,
        'high_priority_tasks': active_tasks.filter(priority='high').count(),
        'overdue_tasks': user.assigned_tasks.filter(get_overdue_tasks(user)).count()
    }