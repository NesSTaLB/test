from django.urls import path
from . import views

app_name = 'crm'

urlpatterns = [
    path('', views.DummyAPIView.as_view(), name='crm-api'),
    # Lead URLs
    path('leads/', views.LeadListCreateView.as_view(), name='lead-list'),
    path('leads/<int:pk>/', views.LeadDetailView.as_view(), name='lead-detail'),
    path('leads/convert/<int:pk>/', views.LeadConvertView.as_view(), name='lead-convert'),
    
    # Opportunity URLs
    path('opportunities/', views.OpportunityListCreateView.as_view(), name='opportunity-list'),
    path('opportunities/<int:pk>/', views.OpportunityDetailView.as_view(), name='opportunity-detail'),
    
    # Activity URLs
    path('activities/', views.ActivityListCreateView.as_view(), name='activity-list'),
    path('activities/<int:pk>/', views.ActivityDetailView.as_view(), name='activity-detail'),
    path('leads/<int:lead_id>/activities/', views.LeadActivityListView.as_view(), name='lead-activities'),
    path('opportunities/<int:opportunity_id>/activities/', views.OpportunityActivityListView.as_view(), name='opportunity-activities'),
    
    # Dashboard URLs
    path('dashboard/summary/', views.CRMDashboardView.as_view(), name='crm-dashboard'),
    path('dashboard/reports/', views.CRMReportView.as_view(), name='crm-reports'),
]