from django.db import models
from users.models import CustomUser
from sales.models import Product

class Supplier(models.Model):
    name = models.CharField(max_length=200, verbose_name="اسم المورد")
    email = models.EmailField(unique=True, verbose_name="البريد الإلكتروني")
    phone = models.CharField(max_length=20, verbose_name="رقم الهاتف")
    address = models.TextField(verbose_name="العنوان")
    company = models.CharField(max_length=200, verbose_name="الشركة")
    tax_number = models.CharField(max_length=50, blank=True, null=True, verbose_name="الرقم الضريبي")
    notes = models.TextField(blank=True, null=True, verbose_name="ملاحظات")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")

    class Meta:
        verbose_name = "المورد"
        verbose_name_plural = "الموردون"

    def __str__(self):
        return self.name

class Purchase(models.Model):
    STATUS_CHOICES = (
        ('draft', 'مسودة'),
        ('ordered', 'تم الطلب'),
        ('received', 'تم الاستلام'),
        ('cancelled', 'ملغي'),
    )

    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, related_name='purchases', verbose_name="المورد")
    purchase_date = models.DateField(verbose_name="تاريخ الشراء")
    reference_number = models.CharField(max_length=50, unique=True, verbose_name="رقم المرجع")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name="الحالة")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="المبلغ الإجمالي")
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="مبلغ الضريبة")
    notes = models.TextField(blank=True, null=True, verbose_name="ملاحظات")
    created_by = models.ForeignKey(CustomUser, on_delete=models.PROTECT, verbose_name="تم الإنشاء بواسطة")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")

    class Meta:
        verbose_name = "عملية الشراء"
        verbose_name_plural = "عمليات الشراء"
        ordering = ['-purchase_date']

    def __str__(self):
        return f"طلب شراء {self.reference_number} - {self.supplier.name}"

class PurchaseItem(models.Model):
    purchase = models.ForeignKey(Purchase, on_delete=models.CASCADE, related_name='items', verbose_name="عملية الشراء")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name="المنتج")
    quantity = models.IntegerField(verbose_name="الكمية")
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="سعر الوحدة")
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="السعر الإجمالي")
    received_quantity = models.IntegerField(default=0, verbose_name="الكمية المستلمة")

    class Meta:
        verbose_name = "عنصر الشراء"
        verbose_name_plural = "عناصر الشراء"

    def __str__(self):
        return f"{self.product.name} - {self.quantity} وحدة"

    def save(self, *args, **kwargs):
        self.total_price = self.quantity * self.unit_price
        super().save(*args, **kwargs)
