from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta
from django.core.mail import send_mail
from django.conf import settings

def calculate_purchase_totals(purchase_items):
    """
    حساب إجماليات عملية الشراء
    """
    subtotal = sum(item.quantity * item.unit_price for item in purchase_items)
    tax = subtotal * 0.15  # 15% VAT
    total = subtotal + tax
    return {
        'subtotal': subtotal,
        'tax': tax,
        'total': total
    }

def process_purchase_receipt(purchase, items_received):
    """
    معالجة استلام المشتريات وتحديث المخزون
    """
    from sales.models import Product
    
    for item in items_received:
        purchase_item = purchase.items.get(id=item['item_id'])
        purchase_item.received_quantity = item['quantity']
        purchase_item.save()
        
        # تحديث المخزون
        product = Product.objects.get(id=purchase_item.product_id)
        product.stock += item['quantity']
        product.save()
    
    # تحديث حالة أمر الشراء
    if all(item.received_quantity == item.quantity for item in purchase.items.all()):
        purchase.status = 'received'
    elif any(item.received_quantity > 0 for item in purchase.items.all()):
        purchase.status = 'partially_received'
    purchase.save()

def send_purchase_order_email(purchase):
    """
    إرسال أمر الشراء بالبريد الإلكتروني
    """
    subject = f'أمر شراء جديد #{purchase.reference_number}'
    message = f"""
    مرحباً {purchase.supplier.name},
    
    نود إرسال أمر الشراء التالي:
    
    رقم المرجع: {purchase.reference_number}
    التاريخ: {purchase.purchase_date}
    
    تفاصيل الطلب:
    {format_purchase_items(purchase.items.all())}
    
    المجموع: {purchase.total_amount}
    
    يرجى تأكيد استلام الطلب والموعد المتوقع للتسليم.
    
    مع التحية،
    {purchase.created_by.get_full_name()}
    """
    
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [purchase.supplier.email],
    )

def format_purchase_items(items):
    """
    تنسيق عناصر أمر الشراء للعرض في البريد الإلكتروني
    """
    formatted_items = []
    for item in items:
        formatted_items.append(
            f"- {item.product.name}: {item.quantity} وحدة × {item.unit_price} = {item.total_price}"
        )
    return "\n".join(formatted_items)

def generate_purchase_report(start_date=None, end_date=None, supplier=None):
    """
    إنشاء تقرير المشتريات
    """
    from .models import Purchase
    
    queryset = Purchase.objects.all()
    
    if start_date:
        queryset = queryset.filter(purchase_date__gte=start_date)
    if end_date:
        queryset = queryset.filter(purchase_date__lte=end_date)
    if supplier:
        queryset = queryset.filter(supplier=supplier)
        
    report = {
        'total_purchases': queryset.count(),
        'total_amount': queryset.aggregate(total=Sum('total_amount'))['total'] or 0,
        'by_status': queryset.values('status').annotate(
            count=Count('id'),
            total=Sum('total_amount')
        ),
        'by_supplier': queryset.values(
            'supplier__name'
        ).annotate(
            count=Count('id'),
            total=Sum('total_amount')
        ),
        'monthly_summary': queryset.annotate(
            month=timezone.datetime.strftime('purchase_date', '%Y-%m')
        ).values('month').annotate(
            count=Count('id'),
            total=Sum('total_amount')
        ).order_by('month')
    }
    
    return report

def analyze_supplier_performance(supplier, period_days=365):
    """
    تحليل أداء المورد
    """
    from .models import Purchase
    start_date = timezone.now().date() - timedelta(days=period_days)
    
    purchases = Purchase.objects.filter(
        supplier=supplier,
        purchase_date__gte=start_date
    )
    
    total_purchases = purchases.count()
    if total_purchases == 0:
        return None
        
    metrics = {
        'total_purchases': total_purchases,
        'total_amount': purchases.aggregate(total=Sum('total_amount'))['total'] or 0,
        'average_delivery_time': calculate_average_delivery_time(purchases),
        'order_accuracy': calculate_order_accuracy(purchases),
        'on_time_delivery': calculate_on_time_delivery(purchases)
    }
    
    return metrics

def calculate_average_delivery_time(purchases):
    """
    حساب متوسط وقت التسليم
    """
    completed_purchases = purchases.filter(status='received')
    if not completed_purchases.exists():
        return 0
        
    total_days = 0
    for purchase in completed_purchases:
        last_receipt = purchase.items.all().order_by('-updated_at').first()
        if last_receipt:
            days = (last_receipt.updated_at.date() - purchase.purchase_date).days
            total_days += days
            
    return total_days / completed_purchases.count()

def calculate_order_accuracy(purchases):
    """
    حساب دقة الطلبات (نسبة العناصر المستلمة بشكل صحيح)
    """
    completed_purchases = purchases.filter(status='received')
    if not completed_purchases.exists():
        return 0
        
    total_items = 0
    correct_items = 0
    
    for purchase in completed_purchases:
        for item in purchase.items.all():
            total_items += 1
            if item.received_quantity == item.quantity:
                correct_items += 1
                
    return (correct_items / total_items) * 100 if total_items > 0 else 0

def calculate_on_time_delivery(purchases):
    """
    حساب نسبة التسليم في الوقت المحدد
    """
    completed_purchases = purchases.filter(status='received')
    if not completed_purchases.exists():
        return 0
        
    on_time = 0
    for purchase in completed_purchases:
        last_receipt = purchase.items.all().order_by('-updated_at').first()
        if last_receipt and last_receipt.updated_at.date() <= purchase.expected_delivery_date:
            on_time += 1
            
    return (on_time / completed_purchases.count()) * 100