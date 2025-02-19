from django.shortcuts import render
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta
from .models import DashboardWidget, UserDashboardPreference, UserWidgetSettings
from .serializers import (DashboardWidgetSerializer, UserDashboardPreferenceSerializer, 
                        UserWidgetSettingsSerializer)
from project_management.models import Project, Task
from sales.models import Sale, Customer
from purchases.models import Purchase
from crm.models import Lead, Opportunity
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
import json

class DashboardWidgetListView(generics.ListCreateAPIView):
    queryset = DashboardWidget.objects.filter(is_active=True)
    serializer_class = DashboardWidgetSerializer
    permission_classes = [permissions.IsAuthenticated]
    ordering_fields = ['position']

class DashboardWidgetDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = DashboardWidget.objects.all()
    serializer_class = DashboardWidgetSerializer
    permission_classes = [permissions.IsAdminUser]

class UserDashboardPreferenceView(generics.RetrieveUpdateAPIView):
    serializer_class = UserDashboardPreferenceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        obj, created = UserDashboardPreference.objects.get_or_create(
            user=self.request.user
        )
        return obj

class UserWidgetSettingsView(generics.ListCreateAPIView):
    serializer_class = UserWidgetSettingsSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserWidgetSettings.objects.filter(
            user_preference__user=self.request.user
        )

    def perform_create(self, serializer):
        user_preference = UserDashboardPreference.objects.get(user=self.request.user)
        serializer.save(user_preference=user_preference)

class DashboardSummaryView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        today = timezone.now().date()
        start_of_month = today.replace(day=1)

        # Projects Summary
        projects = Project.objects.filter(team_members=user)
        tasks = Task.objects.filter(assigned_to=user)
        
        projects_summary = {
            'total_projects': projects.count(),
            'active_projects': projects.filter(status='in_progress').count(),
            'total_tasks': tasks.count(),
            'pending_tasks': tasks.filter(status__in=['todo', 'in_progress']).count(),
            'overdue_tasks': tasks.filter(
                status__in=['todo', 'in_progress'],
                due_date__lt=today
            ).count()
        }

        # Sales Summary
        sales = Sale.objects.filter(sales_person=user)
        sales_summary = {
            'monthly_sales': sales.filter(date__gte=start_of_month).aggregate(
                total=Sum('total_amount'),
                count=Count('id')
            ),
            'pending_sales': sales.filter(status='pending').count()
        }

        # Purchases Summary
        purchases = Purchase.objects.filter(created_by=user)
        purchases_summary = {
            'monthly_purchases': purchases.filter(
                purchase_date__gte=start_of_month
            ).aggregate(
                total=Sum('total_amount'),
                count=Count('id')
            ),
            'pending_orders': purchases.filter(status='ordered').count()
        }

        # CRM Summary
        leads = Lead.objects.filter(assigned_to=user)
        opportunities = Opportunity.objects.filter(assigned_to=user)
        
        crm_summary = {
            'active_leads': leads.exclude(status__in=['won', 'lost']).count(),
            'new_leads_this_month': leads.filter(
                created_at__gte=start_of_month
            ).count(),
            'open_opportunities': opportunities.exclude(
                status__in=['closed_won', 'closed_lost']
            ).count(),
            'opportunity_value': opportunities.exclude(
                status__in=['closed_won', 'closed_lost']
            ).aggregate(total=Sum('value'))['total'] or 0
        }

        return Response({
            'projects': projects_summary,
            'sales': sales_summary,
            'purchases': purchases_summary,
            'crm': crm_summary
        })

class DashboardAnalyticsView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        today = timezone.now().date()
        start_of_year = today.replace(month=1, day=1)
        last_12_months = today - timedelta(days=365)

        # Projects Analytics
        projects_analytics = {
            'projects_by_status': Project.objects.filter(
                team_members=user
            ).values('status').annotate(count=Count('id')),
            'tasks_by_priority': Task.objects.filter(
                assigned_to=user
            ).values('priority').annotate(count=Count('id')),
            'tasks_completion_trend': Task.objects.filter(
                assigned_to=user,
                created_at__gte=last_12_months
            ).values('created_at__month').annotate(
                completed=Count('id', filter={'status': 'completed'}),
                total=Count('id')
            )
        }

        # Sales Analytics
        sales_analytics = {
            'monthly_revenue': Sale.objects.filter(
                sales_person=user,
                date__gte=start_of_year
            ).values('date__month').annotate(
                revenue=Sum('total_amount'),
                count=Count('id')
            ),
            'sales_by_status': Sale.objects.filter(
                sales_person=user
            ).values('status').annotate(
                count=Count('id'),
                total=Sum('total_amount')
            )
        }

        # CRM Analytics
        crm_analytics = {
            'lead_conversion': Lead.objects.filter(
                assigned_to=user
            ).values('status').annotate(count=Count('id')),
            'opportunities_by_stage': Opportunity.objects.filter(
                assigned_to=user
            ).values('status').annotate(
                count=Count('id'),
                value=Sum('value')
            ),
            'conversion_trend': Opportunity.objects.filter(
                assigned_to=user,
                created_at__gte=last_12_months
            ).values('created_at__month').annotate(
                won=Count('id', filter={'status': 'closed_won'}),
                total=Count('id')
            )
        }

        return Response({
            'projects_analytics': projects_analytics,
            'sales_analytics': sales_analytics,
            'crm_analytics': crm_analytics
        })

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # إحصائيات المشاريع
        context['active_projects_count'] = Project.objects.filter(status='in_progress').count()
        context['completed_tasks_count'] = Task.objects.filter(status='completed').count()
        
        # إحصائيات المبيعات
        total_sales = Sale.objects.aggregate(total=Sum('amount'))['total']
        context['total_sales'] = total_sales if total_sales else 0
        
        # عدد العملاء النشطين
        context['active_clients_count'] = Customer.objects.filter(is_active=True).count()
        
        # إحصائيات حالة المشاريع للرسم البياني - تحويل إلى قائمة للـ JSON
        projects_stats = Project.objects.values('status').annotate(count=Count('id'))
        stats_dict = {stat['status']: stat['count'] for stat in projects_stats}
        context['projects_stats'] = json.dumps([
            stats_dict.get('completed', 0),
            stats_dict.get('in_progress', 0),
            stats_dict.get('on_hold', 0)
        ])
        
        # بيانات المبيعات الشهرية
        last_12_months = timezone.now() - timedelta(days=365)
        monthly_sales = Sale.objects.filter(
            date__gte=last_12_months
        ).values('date__month').annotate(
            total=Sum('amount')
        ).order_by('date__month')
        
        months = []
        sales_data = []
        
        for month in monthly_sales:
            months.append(timezone.datetime(2000, month['date__month'], 1).strftime('%B'))
            sales_data.append(float(month['total']))
        
        context['sales_months'] = json.dumps(months)
        context['monthly_sales'] = json.dumps(sales_data)
        
        # المهام العاجلة
        context['urgent_tasks'] = Task.objects.filter(
            status='in_progress',
            priority='high',
            due_date__lte=timezone.now() + timedelta(days=7)
        ).select_related('assigned_to', 'project')[:5]
        
        return context
