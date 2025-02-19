from django.db import models
from users.models import CustomUser

class Customer(models.Model):
    name = models.CharField(max_length=200, verbose_name="اسم العميل")
    email = models.EmailField(unique=True, verbose_name="البريد الإلكتروني")
    phone = models.CharField(max_length=20, verbose_name="رقم الهاتف")
    address = models.TextField(verbose_name="العنوان")
    company = models.CharField(max_length=200, blank=True, null=True, verbose_name="الشركة")
    notes = models.TextField(blank=True, null=True, verbose_name="ملاحظات")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")

    class Meta:
        verbose_name = "العميل"
        verbose_name_plural = "العملاء"

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=200, verbose_name="اسم المنتج")
    description = models.TextField(verbose_name="وصف المنتج")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="السعر")
    sku = models.CharField(max_length=50, unique=True, verbose_name="رمز المنتج")
    stock = models.IntegerField(default=0, verbose_name="المخزون")
    image = models.ImageField(upload_to='products/', blank=True, null=True, verbose_name="صورة المنتج")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")

    class Meta:
        verbose_name = "المنتج"
        verbose_name_plural = "المنتجات"

    def __str__(self):
        return self.name

class Sale(models.Model):
    STATUS_CHOICES = (
        ('pending', 'معلق'),
        ('completed', 'مكتمل'),
        ('cancelled', 'ملغي'),
    )

    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name='sales', verbose_name="العميل")
    sales_person = models.ForeignKey(CustomUser, on_delete=models.PROTECT, verbose_name="مندوب المبيعات")
    date = models.DateField(verbose_name="تاريخ البيع")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="الحالة")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="المبلغ الإجمالي")
    notes = models.TextField(blank=True, null=True, verbose_name="ملاحظات")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")

    class Meta:
        verbose_name = "عملية البيع"
        verbose_name_plural = "عمليات البيع"
        ordering = ['-date']

    def __str__(self):
        return f"بيع {self.id} - {self.customer.name}"

class SaleItem(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='items', verbose_name="عملية البيع")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name="المنتج")
    quantity = models.IntegerField(verbose_name="الكمية")
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="سعر الوحدة")
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="السعر الإجمالي")

    class Meta:
        verbose_name = "عنصر البيع"
        verbose_name_plural = "عناصر البيع"

    def __str__(self):
        return f"{self.product.name} - {self.quantity} وحدة"

    def save(self, *args, **kwargs):
        self.total_price = self.quantity * self.unit_price
        super().save(*args, **kwargs)
