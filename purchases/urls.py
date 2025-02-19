from django.urls import path
from . import views

app_name = 'purchases'

urlpatterns = [
    # Supplier URLs
    path('suppliers/', views.SupplierListCreateView.as_view(), name='supplier-list'),
    path('suppliers/<int:pk>/', views.SupplierDetailView.as_view(), name='supplier-detail'),
    
    # Purchase URLs
    path('purchases/', views.PurchaseListCreateView.as_view(), name='purchase-list'),
    path('purchases/<int:pk>/', views.PurchaseDetailView.as_view(), name='purchase-detail'),
    path('purchases/<int:purchase_id>/items/', views.PurchaseItemListCreateView.as_view(), name='purchase-item-list'),
    path('purchases/items/<int:pk>/', views.PurchaseItemDetailView.as_view(), name='purchase-item-detail'),
    
    # Dashboard URLs
    path('dashboard/summary/', views.PurchaseDashboardView.as_view(), name='purchase-dashboard'),
    path('dashboard/reports/', views.PurchaseReportView.as_view(), name='purchase-reports'),
]