from django.urls import path
from . import views

app_name = 'sales'

urlpatterns = [
    # Customer URLs
    path('customers/', views.CustomerListCreateView.as_view(), name='customer-list'),
    path('customers/<int:pk>/', views.CustomerDetailView.as_view(), name='customer-detail'),
    
    # Product URLs
    path('products/', views.ProductListCreateView.as_view(), name='product-list'),
    path('products/<int:pk>/', views.ProductDetailView.as_view(), name='product-detail'),
    
    # Sale URLs
    path('sales/', views.SaleListCreateView.as_view(), name='sale-list'),
    path('sales/<int:pk>/', views.SaleDetailView.as_view(), name='sale-detail'),
    path('sales/<int:sale_id>/items/', views.SaleItemListCreateView.as_view(), name='sale-item-list'),
    path('sales/items/<int:pk>/', views.SaleItemDetailView.as_view(), name='sale-item-detail'),
    
    # Dashboard URLs
    path('dashboard/summary/', views.SalesDashboardView.as_view(), name='sales-dashboard'),
    path('dashboard/reports/', views.SalesReportView.as_view(), name='sales-reports'),
]