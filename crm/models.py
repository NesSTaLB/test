from django.db import models
from users.models import CustomUser
from sales.models import Customer

class Lead(models.Model):
    STATUS_CHOICES = (
        ('new', 'جديد'),
        ('contacted', 'تم التواصل'),
        ('qualified', 'مؤهل'),
        ('proposal', 'تم تقديم عرض'),
        ('negotiation', 'قيد التفاوض'),
        ('won', 'تم الكسب'),
        ('lost', 'خسارة'),
    )

    SOURCE_CHOICES = (
        ('website', 'الموقع الإلكتروني'),
        ('referral', 'إحالة'),
        ('social_media', 'وسائل التواصل الاجتماعي'),
        ('direct', 'مباشر'),
        ('other', 'أخرى'),
    )

    name = models.CharField(max_length=200, verbose_name="الاسم")
    company = models.CharField(max_length=200, blank=True, null=True, verbose_name="الشركة")
    email = models.EmailField(verbose_name="البريد الإلكتروني")
    phone = models.CharField(max_length=20, verbose_name="رقم الهاتف")
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, verbose_name="المصدر")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new', verbose_name="الحالة")
    assigned_to = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='leads', verbose_name="مسند إلى")
    notes = models.TextField(blank=True, null=True, verbose_name="ملاحظات")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")

    class Meta:
        verbose_name = "العميل المحتمل"
        verbose_name_plural = "العملاء المحتملون"
        ordering = ['-created_at']

    def __str__(self):
        return self.name

class Opportunity(models.Model):
    STATUS_CHOICES = (
        ('identified', 'تم التحديد'),
        ('qualified', 'مؤهل'),
        ('proposal', 'تم تقديم عرض'),
        ('negotiation', 'قيد التفاوض'),
        ('closed_won', 'مغلق - ناجح'),
        ('closed_lost', 'مغلق - خاسر'),
    )

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='opportunities', verbose_name="العميل")
    title = models.CharField(max_length=200, verbose_name="العنوان")
    description = models.TextField(verbose_name="الوصف")
    value = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="القيمة المتوقعة")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='identified', verbose_name="الحالة")
    expected_close_date = models.DateField(verbose_name="تاريخ الإغلاق المتوقع")
    assigned_to = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='opportunities', verbose_name="مسند إلى")
    probability = models.IntegerField(default=50, verbose_name="احتمالية النجاح (%)")
    notes = models.TextField(blank=True, null=True, verbose_name="ملاحظات")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")

    class Meta:
        verbose_name = "الفرصة"
        verbose_name_plural = "الفرص"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.customer.name}"

class Activity(models.Model):
    TYPE_CHOICES = (
        ('call', 'اتصال'),
        ('meeting', 'اجتماع'),
        ('email', 'بريد إلكتروني'),
        ('note', 'ملاحظة'),
        ('task', 'مهمة'),
    )

    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, null=True, blank=True, related_name='activities', verbose_name="العميل المحتمل")
    opportunity = models.ForeignKey(Opportunity, on_delete=models.CASCADE, null=True, blank=True, related_name='activities', verbose_name="الفرصة")
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, verbose_name="النوع")
    subject = models.CharField(max_length=200, verbose_name="الموضوع")
    description = models.TextField(verbose_name="الوصف")
    date = models.DateTimeField(verbose_name="التاريخ")
    created_by = models.ForeignKey(CustomUser, on_delete=models.PROTECT, related_name='created_activities', verbose_name="تم الإنشاء بواسطة")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")

    class Meta:
        verbose_name = "النشاط"
        verbose_name_plural = "الأنشطة"
        ordering = ['-date']

    def __str__(self):
        return f"{self.get_type_display()} - {self.subject}"
