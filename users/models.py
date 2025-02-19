from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'مدير النظام'),
        ('manager', 'مدير'),
        ('employee', 'موظف'),
    )
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='employee', verbose_name="الدور")
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="رقم الهاتف")
    address = models.TextField(blank=True, null=True, verbose_name="العنوان")
    department = models.CharField(max_length=100, blank=True, null=True, verbose_name="القسم")
    
    class Meta:
        verbose_name = "المستخدم"
        verbose_name_plural = "المستخدمين"
        
    def __str__(self):
        return self.get_full_name() or self.username
