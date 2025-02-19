from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.html import format_html

class Project(models.Model):
    STATUS_CHOICES = (
        ('new', 'جديد'),
        ('in_progress', 'قيد التنفيذ'),
        ('completed', 'مكتمل'),
        ('on_hold', 'معلق'),
        ('cancelled', 'ملغي'),
    )
    
    name = models.CharField(max_length=200, verbose_name="اسم المشروع")
    description = models.TextField(verbose_name="وصف المشروع")
    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='managed_projects',
        verbose_name="مدير المشروع"
    )
    team_members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='project_teams',
        blank=True,
        verbose_name="أعضاء الفريق"
    )
    project_plans = models.FileField(
        upload_to='projects/plans/',
        null=True,
        blank=True,
        verbose_name="مخططات المشروع"
    )
    project_images = models.ImageField(
        upload_to='projects/images/',
        null=True,
        blank=True,
        verbose_name="صور المشروع"
    )
    start_date = models.DateField(verbose_name="تاريخ البدء")
    end_date = models.DateField(verbose_name="تاريخ الانتهاء المتوقع")
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='new',
        verbose_name="الحالة"
    )
    budget = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="الميزانية"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")

    def get_status_display_with_color(self):
        status_colors = {
            'new': '#3498db',
            'in_progress': '#f1c40f',
            'completed': '#2ecc71',
            'on_hold': '#95a5a6',
            'cancelled': '#e74c3c',
        }
        color = status_colors.get(self.status, '#666666')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            self.get_status_display()
        )
    
    @property
    def progress_percentage(self):
        total_tasks = self.tasks.count()
        if total_tasks == 0:
            return 0
        completed_tasks = self.tasks.filter(status='completed').count()
        return int((completed_tasks / total_tasks) * 100)
    
    @property
    def is_overdue(self):
        return self.end_date < timezone.now().date() and self.status != 'completed'
    
    def get_team_members_display(self):
        return ", ".join([str(member) for member in self.team_members.all()])
    
    def get_budget_display(self):
        if self.budget:
            return f"{self.budget:,.2f} ريال"
        return "غير محدد"

    class Meta:
        verbose_name = "المشروع"
        verbose_name_plural = "المشاريع"
        ordering = ['-created_at']

    def __str__(self):
        return self.name

class Task(models.Model):
    STATUS_CHOICES = (
        ('todo', 'للتنفيذ'),
        ('in_progress', 'قيد التنفيذ'),
        ('review', 'قيد المراجعة'),
        ('completed', 'مكتمل'),
    )
    
    PRIORITY_CHOICES = (
        ('low', 'منخفضة'),
        ('medium', 'متوسطة'),
        ('high', 'عالية'),
    )
    
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='tasks',
        verbose_name="المشروع"
    )
    title = models.CharField(max_length=200, verbose_name="عنوان المهمة")
    description = models.TextField(verbose_name="وصف المهمة")
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_tasks',
        verbose_name="مسند إلى"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='todo',
        verbose_name="الحالة"
    )
    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default='medium',
        verbose_name="الأولوية"
    )
    start_date = models.DateField(verbose_name="تاريخ البدء")
    due_date = models.DateField(verbose_name="تاريخ الاستحقاق")
    estimated_hours = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="الساعات المقدرة"
    )
    actual_hours = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="الساعات الفعلية"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name="تاريخ الإكمال")

    def get_priority_badge(self):
        priority_colors = {
            'low': '#2ecc71',
            'medium': '#f1c40f',
            'high': '#e74c3c',
        }
        color = priority_colors.get(self.priority, '#95a5a6')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            color,
            self.get_priority_display()
        )
    
    def get_status_with_icon(self):
        status_icons = {
            'todo': '📋',
            'in_progress': '⚡',
            'review': '👀',
            'completed': '✅',
        }
        icon = status_icons.get(self.status, '❔')
        return format_html(
            '{} {}',
            icon,
            self.get_status_display()
        )
    
    @property
    def time_remaining(self):
        if self.due_date:
            days = (self.due_date - timezone.now().date()).days
            if days < 0:
                return "متأخر"
            elif days == 0:
                return "اليوم"
            else:
                return f"{days} يوم"
        return "غير محدد"
    
    @property
    def completion_status(self):
        if self.status == 'completed':
            if self.completed_at:
                if self.completed_at.date() <= self.due_date:
                    return "تم في الوقت المحدد"
                return "تم متأخراً"
            return "مكتمل"
        return "قيد التنفيذ"
    
    def save(self, *args, **kwargs):
        if self.status == 'completed' and not self.completed_at:
            self.completed_at = timezone.now()
        elif self.status != 'completed':
            self.completed_at = None
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "المهمة"
        verbose_name_plural = "المهام"
        ordering = ['-created_at']

    def __str__(self):
        return self.title
