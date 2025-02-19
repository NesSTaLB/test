from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta
from django.core.mail import send_mail
from django.conf import settings

def calculate_sale_totals(sale_items):
    """
    حساب إجماليات عملية البيع
    """
    total = sum(item.quantity * item.unit_price for item in sale_items)
    return {
        'subtotal': total,
        'tax': total * 0.15,  # 15% ضريبة القيمة المضافة
        'total': total * 1.15
    }

def update_product_stock(product, quantity, operation='decrease'):
    """
    تحديث مخزون المنتج
    """
    if operation == 'decrease':
        product.stock -= quantity
    else:
        product.stock += quantity
    product.save()

def check_low_stock_products(threshold=10):
    """
    التحقق من المنتجات التي وصلت لحد المخزون المنخفض
    """
    from .models import Product
    return Product.objects.filter(stock__lte=threshold)

def send_low_stock_notification(product):
    """
    إرسال إشعار بانخفاض المخزون
    """
    subject = f'تنبيه: انخفاض مخزون المنتج - {product.name}'
    message = f"""
    تنبيه: المنتج التالي وصل إلى مستوى منخفض من المخزون:
    
    المنتج: {product.name}
    الكمية المتبقية: {product.stock}
    رمز المنتج: {product.sku}
    
    يرجى إعادة طلب هذا المنتج في أقرب وقت.
    """
    
    admin_emails = ['admin@example.com']  # يمكن تحديث هذه القائمة حسب الحاجة
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        admin_emails,
    )

def generate_sales_report(start_date=None, end_date=None):
    """
    إنشاء تقرير المبيعات
    """
    from .models import Sale
    
    if not start_date:
        start_date = timezone.now().date() - timedelta(days=30)
    if not end_date:
        end_date = timezone.now().date()
        
    sales = Sale.objects.filter(
        date__range=[start_date, end_date]
    )
    
    report = {
        'total_sales': sales.count(),
        'total_revenue': sales.aggregate(total=Sum('total_amount'))['total'] or 0,
        'sales_by_status': sales.values('status').annotate(
            count=Count('id'),
            total=Sum('total_amount')
        ),
        'daily_sales': sales.values('date').annotate(
            count=Count('id'),
            total=Sum('total_amount')
        ).order_by('date')
    }
    
    return report

def calculate_customer_metrics(customer):
    """
    حساب مؤشرات العميل
    """
    from .models import Sale
    
    sales = Sale.objects.filter(customer=customer)
    first_purchase = sales.order_by('date').first()
    last_purchase = sales.order_by('-date').first()
    
    metrics = {
        'total_purchases': sales.count(),
        'total_spent': sales.aggregate(total=Sum('total_amount'))['total'] or 0,
        'average_purchase': (sales.aggregate(total=Sum('total_amount'))['total'] or 0) / sales.count() if sales.exists() else 0,
        'first_purchase_date': first_purchase.date if first_purchase else None,
        'last_purchase_date': last_purchase.date if last_purchase else None,
        'purchase_frequency': calculate_purchase_frequency(customer)
    }
    
    return metrics

def calculate_purchase_frequency(customer):
    """
    حساب معدل تكرار الشراء للعميل
    """
    from .models import Sale
    
    sales = Sale.objects.filter(customer=customer).order_by('date')
    if sales.count() < 2:
        return 0
        
    first_purchase = sales.first().date
    last_purchase = sales.last().date
    days_between = (last_purchase - first_purchase).days
    
    if days_between == 0:
        return 0
        
    return sales.count() / days_between  # متوسط عدد المشتريات في اليوم