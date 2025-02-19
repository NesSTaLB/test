from django.shortcuts import render
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Sum, Count, Avg, F, Q
from django.utils import timezone
from datetime import timedelta
from .models import Customer, Product, Sale, SaleItem
from .serializers import (CustomerSerializer, ProductSerializer, 
                        SaleSerializer, SaleCreateSerializer, SaleItemSerializer)
from .utils import generate_sales_report, calculate_customer_metrics

class CustomerListCreateView(generics.ListCreateAPIView):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [permissions.IsAuthenticated]
    search_fields = ['name', 'email', 'phone', 'company']
    ordering_fields = ['name', 'created_at']

class CustomerDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [permissions.IsAuthenticated]

class ProductListCreateView(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]
    search_fields = ['name', 'sku', 'description']
    filterset_fields = ['stock']
    ordering_fields = ['name', 'price', 'stock']

class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]

class SaleListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    search_fields = ['customer__name', 'reference_number']
    filterset_fields = ['status', 'date']
    ordering_fields = ['date', 'total_amount']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return SaleCreateSerializer
        return SaleSerializer

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Sale.objects.all()
        return Sale.objects.filter(sales_person=user)

class SaleDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Sale.objects.all()
    serializer_class = SaleSerializer
    permission_classes = [permissions.IsAuthenticated]

class SaleItemListCreateView(generics.ListCreateAPIView):
    serializer_class = SaleItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        sale_id = self.kwargs.get('sale_id')
        return SaleItem.objects.filter(sale_id=sale_id)

    def perform_create(self, serializer):
        sale_id = self.kwargs.get('sale_id')
        serializer.save(sale_id=sale_id)

class SaleItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = SaleItem.objects.all()
    serializer_class = SaleItemSerializer
    permission_classes = [permissions.IsAuthenticated]

class SalesDashboardView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        today = timezone.now().date()
        start_of_month = today.replace(day=1)
        last_30_days = today - timedelta(days=30)

        sales_query = Sale.objects.filter(sales_person=request.user)
        
        stats = {
            'today_sales': sales_query.filter(date=today).aggregate(
                total=Sum('total_amount'),
                count=Count('id')
            ),
            'month_sales': sales_query.filter(date__gte=start_of_month).aggregate(
                total=Sum('total_amount'),
                count=Count('id')
            ),
            'last_30_days': sales_query.filter(date__gte=last_30_days).aggregate(
                total=Sum('total_amount'),
                count=Count('id')
            ),
            'status_breakdown': {
                status: sales_query.filter(status=status).count()
                for status, _ in Sale.STATUS_CHOICES
            }
        }
        
        return Response(stats)

class SalesReportView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        start_date = request.query_params.get('start_date', None)
        end_date = request.query_params.get('end_date', None)
        
        sales_query = Sale.objects.all()
        if start_date:
            sales_query = sales_query.filter(date__gte=start_date)
        if end_date:
            sales_query = sales_query.filter(date__lte=end_date)

        report = {
            'total_sales': sales_query.aggregate(
                total=Sum('total_amount'),
                count=Count('id')
            ),
            'sales_by_product': SaleItem.objects.filter(
                sale__in=sales_query
            ).values(
                'product__name'
            ).annotate(
                total_quantity=Sum('quantity'),
                total_amount=Sum('total_price')
            ),
            'sales_by_customer': sales_query.values(
                'customer__name'
            ).annotate(
                total_amount=Sum('total_amount'),
                total_sales=Count('id')
            )
        }
        
        return Response(report)

class SalesAnalyticsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        period = request.query_params.get('period', '30')  # Default to 30 days
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=int(period))
        
        sales_query = Sale.objects.filter(date__range=[start_date, end_date])
        if request.user.role != 'admin':
            sales_query = sales_query.filter(sales_person=request.user)

        analytics = {
            'summary': {
                'total_sales': sales_query.count(),
                'total_revenue': sales_query.aggregate(total=Sum('total_amount'))['total'] or 0,
                'average_sale_value': sales_query.aggregate(avg=Avg('total_amount'))['avg'] or 0,
            },
            'trends': {
                'daily_sales': sales_query.values('date').annotate(
                    count=Count('id'),
                    revenue=Sum('total_amount')
                ).order_by('date'),
                'by_status': sales_query.values('status').annotate(
                    count=Count('id'),
                    revenue=Sum('total_amount')
                ),
            },
            'top_products': SaleItem.objects.filter(
                sale__in=sales_query
            ).values(
                'product__name'
            ).annotate(
                units_sold=Sum('quantity'),
                revenue=Sum('total_price')
            ).order_by('-revenue')[:10],
            'top_customers': sales_query.values(
                'customer__name'
            ).annotate(
                purchase_count=Count('id'),
                total_spent=Sum('total_amount')
            ).order_by('-total_spent')[:10]
        }
        
        return Response(analytics)

class ProductPerformanceView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        period = request.query_params.get('period', '30')
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=int(period))

        products = Product.objects.all()
        sales_data = SaleItem.objects.filter(
            sale__date__range=[start_date, end_date]
        )

        performance = {
            'product_metrics': products.annotate(
                units_sold=Sum('saleitem__quantity'),
                revenue=Sum('saleitem__total_price'),
                sale_count=Count('saleitem')
            ).values(
                'id', 'name', 'stock', 'price',
                'units_sold', 'revenue', 'sale_count'
            ),
            'low_stock_alerts': products.filter(
                stock__lte=F('minimum_stock')
            ).values('id', 'name', 'stock', 'minimum_stock'),
            'best_sellers': sales_data.values(
                'product__name'
            ).annotate(
                units_sold=Sum('quantity'),
                revenue=Sum('total_price')
            ).order_by('-units_sold')[:5]
        }
        
        return Response(performance)

class CustomerInsightsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, customer_id=None):
        if customer_id:
            try:
                customer = Customer.objects.get(id=customer_id)
                metrics = calculate_customer_metrics(customer)
                return Response(metrics)
            except Customer.DoesNotExist:
                return Response({'error': 'العميل غير موجود'}, status=404)

        period = request.query_params.get('period', '365')  # Default to yearly
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=int(period))

        customers = Customer.objects.filter(
            sales__date__range=[start_date, end_date]
        ).distinct()

        insights = {
            'customer_segments': {
                'total_customers': customers.count(),
                'new_customers': customers.filter(
                    created_at__range=[start_date, end_date]
                ).count(),
                'active_customers': customers.filter(
                    sales__date__range=[start_date, end_date]
                ).distinct().count(),
            },
            'purchase_patterns': {
                'frequency': customers.annotate(
                    purchase_count=Count('sales')
                ).values(
                    'purchase_count'
                ).annotate(
                    customer_count=Count('id')
                ).order_by('purchase_count'),
                'value_segments': customers.annotate(
                    total_spent=Sum('sales__total_amount')
                ).values(
                    'id', 'name', 'total_spent'
                ).order_by('-total_spent'),
            },
            'retention': calculate_customer_retention(start_date, end_date)
        }
        
        return Response(insights)

def calculate_customer_retention(start_date, end_date):
    previous_period_start = start_date - timedelta(days=(end_date - start_date).days)
    
    previous_customers = set(
        Sale.objects.filter(
            date__range=[previous_period_start, start_date]
        ).values_list('customer_id', flat=True)
    )
    
    current_customers = set(
        Sale.objects.filter(
            date__range=[start_date, end_date]
        ).values_list('customer_id', flat=True)
    )
    
    retained = len(previous_customers.intersection(current_customers))
    
    return {
        'retention_rate': (retained / len(previous_customers) * 100) if previous_customers else 0,
        'retained_customers': retained,
        'lost_customers': len(previous_customers - current_customers),
        'new_customers': len(current_customers - previous_customers)
    }
