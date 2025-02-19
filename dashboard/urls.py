from django.urls import path
from . import views
from .views import DashboardView

app_name = 'dashboard'

urlpatterns = [
    path('', DashboardView.as_view(), name='index'),
    path('widgets/', views.DashboardWidgetListView.as_view(), name='widget-list'),
    path('widgets/<int:pk>/', views.DashboardWidgetDetailView.as_view(), name='widget-detail'),
    path('preferences/', views.UserDashboardPreferenceView.as_view(), name='user-preferences'),
    path('widget-settings/', views.UserWidgetSettingsView.as_view(), name='widget-settings'),
    path('summary/', views.DashboardSummaryView.as_view(), name='dashboard-summary'),
    path('analytics/', views.DashboardAnalyticsView.as_view(), name='dashboard-analytics'),
]