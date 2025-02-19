from django.shortcuts import render
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta
from .models import Supplier, Purchase, PurchaseItem
from .serializers import (SupplierSerializer, PurchaseSerializer, 
                        PurchaseCreateSerializer, PurchaseItemSerializer)
from rest_framework.views import APIView
from django.db.models import Sum, Count, Avg, F, Q
from .utils import (
    generate_purchase_report,
    analyze_supplier_performance,
    calculate_purchase_totals
)

class SupplierListCreateView(generics.ListCreateAPIView):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    permission_classes = [permissions.IsAuthenticated]
    search_fields = ['name', 'email', 'phone', 'company']
    ordering_fields = ['name', 'created_at']

class SupplierDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    permission_classes = [permissions.IsAuthenticated]

class PurchaseListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    search_fields = ['reference_number', 'supplier__name']
    filterset_fields = ['status', 'purchase_date']
    ordering_fields = ['purchase_date', 'total_amount']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return PurchaseCreateSerializer
        return PurchaseSerializer

    def get_queryset(self):
        if self.request.user.role == 'admin':
            return Purchase.objects.all()
        return Purchase.objects.filter(created_by=self.request.user)

class PurchaseDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Purchase.objects.all()
    serializer_class = PurchaseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.role == 'admin':
            return Purchase.objects.all()
        return Purchase.objects.filter(created_by=self.request.user)

class PurchaseItemListCreateView(generics.ListCreateAPIView):
    serializer_class = PurchaseItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        purchase_id = self.kwargs.get('purchase_id')
        return PurchaseItem.objects.filter(purchase_id=purchase_id)

    def perform_create(self, serializer):
        purchase_id = self.kwargs.get('purchase_id')
        serializer.save(purchase_id=purchase_id)

class PurchaseItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = PurchaseItem.objects.all()
    serializer_class = PurchaseItemSerializer
    permission_classes = [permissions.IsAuthenticated]

class PurchaseDashboardView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        today = timezone.now().date()
        start_of_month = today.replace(day=1)
        last_30_days = today - timedelta(days=30)

        purchases_query = Purchase.objects.all()
        if request.user.role != 'admin':
            purchases_query = purchases_query.filter(created_by=request.user)

        stats = {
            'today_purchases': purchases_query.filter(purchase_date=today).aggregate(
                total=Sum('total_amount'),
                count=Count('id')
            ),
            'month_purchases': purchases_query.filter(purchase_date__gte=start_of_month).aggregate(
                total=Sum('total_amount'),
                count=Count('id')
            ),
            'last_30_days': purchases_query.filter(purchase_date__gte=last_30_days).aggregate(
                total=Sum('total_amount'),
                count=Count('id')
            ),
            'status_breakdown': {
                status: purchases_query.filter(status=status).count()
                for status, _ in Purchase.STATUS_CHOICES
            }
        }
        
        return Response(stats)

class PurchaseReportView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        start_date = request.query_params.get('start_date', None)
        end_date = request.query_params.get('end_date', None)
        
        purchases_query = Purchase.objects.all()
        if request.user.role != 'admin':
            purchases_query = purchases_query.filter(created_by=request.user)
            
        if start_date:
            purchases_query = purchases_query.filter(purchase_date__gte=start_date)
        if end_date:
            purchases_query = purchases_query.filter(purchase_date__lte=end_date)

        report = {
            'total_purchases': purchases_query.aggregate(
                total=Sum('total_amount'),
                count=Count('id')
            ),
            'purchases_by_supplier': purchases_query.values(
                'supplier__name'
            ).annotate(
                total_amount=Sum('total_amount'),
                total_purchases=Count('id')
            ),
            'items_summary': PurchaseItem.objects.filter(
                purchase__in=purchases_query
            ).values(
                'product__name'
            ).annotate(
                total_quantity=Sum('quantity'),
                total_amount=Sum('total_price')
            )
        }
        
        return Response(report)

class PurchaseAnalyticsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        period = request.query_params.get('period', '30')
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=int(period))
        
        purchases_query = Purchase.objects.filter(
            purchase_date__range=[start_date, end_date]
        )
        if request.user.role != 'admin':
            purchases_query = purchases_query.filter(created_by=request.user)

        analytics = {
            'summary': {
                'total_purchases': purchases_query.count(),
                'total_spent': purchases_query.aggregate(
                    total=Sum('total_amount')
                )['total'] or 0,
                'average_purchase_value': purchases_query.aggregate(
                    avg=Avg('total_amount')
                )['avg'] or 0,
            },
            'trends': {
                'daily_purchases': purchases_query.values(
                    'purchase_date'
                ).annotate(
                    count=Count('id'),
                    total=Sum('total_amount')
                ).order_by('purchase_date'),
                'by_status': purchases_query.values('status').annotate(
                    count=Count('id'),
                    total=Sum('total_amount')
                ),
            },
            'supplier_analysis': purchases_query.values(
                'supplier__name'
            ).annotate(
                purchase_count=Count('id'),
                total_amount=Sum('total_amount'),
                average_amount=Avg('total_amount')
            ).order_by('-total_amount'),
            'top_products': PurchaseItem.objects.filter(
                purchase__in=purchases_query
            ).values(
                'product__name'
            ).annotate(
                quantity=Sum('quantity'),
                total_cost=Sum('total_price')
            ).order_by('-total_cost')[:10]
        }
        
        return Response(analytics)

class SupplierPerformanceView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, supplier_id=None):
        period = request.query_params.get('period', '365')
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=int(period))

        if supplier_id:
            try:
                supplier = Supplier.objects.get(id=supplier_id)
                performance = analyze_supplier_performance(supplier, int(period))
                return Response(performance)
            except Supplier.DoesNotExist:
                return Response(
                    {'error': 'المورد غير موجود'},
                    status=404
                )

        suppliers = Supplier.objects.filter(
            purchases__purchase_date__range=[start_date, end_date]
        ).distinct()

        performance_metrics = {
            'supplier_rankings': suppliers.annotate(
                purchase_count=Count('purchases'),
                total_spent=Sum('purchases__total_amount'),
                average_delivery_time=Avg(
                    F('purchases__actual_delivery_date') - F('purchases__purchase_date')
                ),
                on_time_delivery_rate=Count(
                    'purchases',
                    filter=Q(
                        purchases__actual_delivery_date__lte=F('purchases__expected_delivery_date')
                    )
                ) * 100.0 / Count('purchases')
            ).values(
                'id', 'name', 'purchase_count', 'total_spent',
                'average_delivery_time', 'on_time_delivery_rate'
            ).order_by('-total_spent'),
            'quality_metrics': calculate_quality_metrics(suppliers, start_date, end_date),
            'cost_analysis': calculate_cost_analysis(suppliers, start_date, end_date)
        }
        
        return Response(performance_metrics)

class InventoryReportsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        from sales.models import Product
        
        products = Product.objects.all()
        low_stock_threshold = request.query_params.get('low_stock_threshold', 10)

        inventory_status = {
            'summary': {
                'total_products': products.count(),
                'low_stock_products': products.filter(
                    stock__lte=low_stock_threshold
                ).count(),
                'out_of_stock_products': products.filter(stock=0).count(),
                'total_inventory_value': sum(
                    product.stock * product.price for product in products
                )
            },
            'stock_alerts': products.filter(
                stock__lte=F('minimum_stock')
            ).values(
                'id', 'name', 'stock', 'minimum_stock', 'price'
            ),
            'inventory_turnover': calculate_inventory_turnover(products),
            'purchase_suggestions': generate_purchase_suggestions(products)
        }
        
        return Response(inventory_status)

def calculate_quality_metrics(suppliers, start_date, end_date):
    metrics = {}
    for supplier in suppliers:
        purchases = Purchase.objects.filter(
            supplier=supplier,
            purchase_date__range=[start_date, end_date]
        )
        
        total_items = PurchaseItem.objects.filter(purchase__in=purchases).count()
        defective_items = PurchaseItem.objects.filter(
            purchase__in=purchases,
            quality_issues=True
        ).count()
        
        metrics[supplier.id] = {
            'supplier_name': supplier.name,
            'defect_rate': (defective_items / total_items * 100) if total_items > 0 else 0,
            'return_rate': calculate_return_rate(purchases),
            'quality_rating': calculate_quality_rating(purchases)
        }
    
    return metrics

def calculate_cost_analysis(suppliers, start_date, end_date):
    analysis = {}
    for supplier in suppliers:
        purchases = Purchase.objects.filter(
            supplier=supplier,
            purchase_date__range=[start_date, end_date]
        )
        
        analysis[supplier.id] = {
            'supplier_name': supplier.name,
            'average_unit_cost': calculate_average_unit_cost(purchases),
            'cost_variance': calculate_cost_variance(purchases),
            'payment_history': analyze_payment_history(purchases)
        }
    
    return analysis

def calculate_inventory_turnover(products):
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=365)
    
    turnover = {}
    for product in products:
        sold_quantity = SaleItem.objects.filter(
            product=product,
            sale__date__range=[start_date, end_date]
        ).aggregate(total=Sum('quantity'))['total'] or 0
        
        average_inventory = (
            product.stock + 
            PurchaseItem.objects.filter(
                product=product,
                purchase__purchase_date__range=[start_date, end_date]
            ).aggregate(total=Sum('quantity'))['total'] or 0
        ) / 2
        
        turnover[product.id] = {
            'product_name': product.name,
            'sold_quantity': sold_quantity,
            'average_inventory': average_inventory,
            'turnover_rate': sold_quantity / average_inventory if average_inventory > 0 else 0,
            'days_on_hand': (average_inventory / sold_quantity * 365) if sold_quantity > 0 else 0
        }
    
    return turnover

def generate_purchase_suggestions(products):
    suggestions = []
    for product in products:
        if product.stock <= product.minimum_stock:
            avg_monthly_sales = calculate_average_monthly_sales(product)
            suggested_quantity = max(
                product.minimum_stock * 2,
                avg_monthly_sales * 1.5
            ) - product.stock
            
            if suggested_quantity > 0:
                suggestions.append({
                    'product_id': product.id,
                    'product_name': product.name,
                    'current_stock': product.stock,
                    'minimum_stock': product.minimum_stock,
                    'suggested_quantity': suggested_quantity,
                    'estimated_cost': suggested_quantity * product.price
                })
    
    return suggestions

def calculate_average_monthly_sales(product):
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=90)  # Last 3 months
    
    total_sales = SaleItem.objects.filter(
        product=product,
        sale__date__range=[start_date, end_date]
    ).aggregate(total=Sum('quantity'))['total'] or 0
    
    return total_sales / 3  # Average monthly sales
