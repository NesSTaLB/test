from django.db import models
from users.models import CustomUser

class DashboardWidget(models.Model):
    WIDGET_TYPES = (
        ('sales_chart', 'رسم بياني للمبيعات'),
        ('revenue_chart', 'رسم بياني للإيرادات'),
        ('tasks_summary', 'ملخص المهام'),
        ('projects_status', 'حالة المشاريع'),
        ('top_customers', 'كبار العملاء'),
        ('inventory_alerts', 'تنبيهات المخزون'),
    )

    title = models.CharField(max_length=100, verbose_name="العنوان")
    widget_type = models.CharField(max_length=20, choices=WIDGET_TYPES, verbose_name="نوع العنصر")
    position = models.IntegerField(default=0, verbose_name="الترتيب")
    is_active = models.BooleanField(default=True, verbose_name="نشط")
    refresh_interval = models.IntegerField(default=300, verbose_name="فترة التحديث (بالثواني)")
    settings = models.JSONField(default=dict, blank=True, verbose_name="الإعدادات")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")

    class Meta:
        verbose_name = "عنصر لوحة التحكم"
        verbose_name_plural = "عناصر لوحة التحكم"
        ordering = ['position']

    def __str__(self):
        return self.title

class UserDashboardPreference(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='dashboard_preference', verbose_name="المستخدم")
    widgets = models.ManyToManyField(DashboardWidget, through='UserWidgetSettings', verbose_name="العناصر")
    layout = models.JSONField(default=dict, verbose_name="تخطيط اللوحة")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")

    class Meta:
        verbose_name = "تفضيلات لوحة التحكم"
        verbose_name_plural = "تفضيلات لوحة التحكم"

    def __str__(self):
        return f"تفضيلات {self.user.username}"

class UserWidgetSettings(models.Model):
    user_preference = models.ForeignKey(UserDashboardPreference, on_delete=models.CASCADE, verbose_name="تفضيلات المستخدم")
    widget = models.ForeignKey(DashboardWidget, on_delete=models.CASCADE, verbose_name="العنصر")
    position = models.IntegerField(verbose_name="الموقع")
    is_visible = models.BooleanField(default=True, verbose_name="مرئي")
    settings = models.JSONField(default=dict, blank=True, verbose_name="الإعدادات")

    class Meta:
        verbose_name = "إعدادات عنصر المستخدم"
        verbose_name_plural = "إعدادات عناصر المستخدم"
        ordering = ['position']
        unique_together = ['user_preference', 'widget']

    def __str__(self):
        return f"{self.widget.title} - {self.user_preference.user.username}"
