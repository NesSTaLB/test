from django.shortcuts import render
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Sum, Count, Avg, F, Q
from django.utils import timezone
from datetime import timedelta
from .models import Lead, Opportunity, Activity
from sales.models import Customer, Sale
from .serializers import (LeadSerializer, OpportunitySerializer, 
                        ActivitySerializer, LeadConvertSerializer)

class LeadListCreateView(generics.ListCreateAPIView):
    serializer_class = LeadSerializer
    permission_classes = [permissions.IsAuthenticated]
    search_fields = ['name', 'company', 'email', 'phone']
    filterset_fields = ['status', 'source']
    ordering_fields = ['created_at', 'name']

    def get_queryset(self):
        if self.request.user.role == 'admin':
            return Lead.objects.all()
        return Lead.objects.filter(
            Q(assigned_to=self.request.user) | 
            Q(assigned_to=None)
        )

class LeadDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Lead.objects.all()
    serializer_class = LeadSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.role == 'admin':
            return Lead.objects.all()
        return Lead.objects.filter(assigned_to=self.request.user)

class LeadConvertView(generics.UpdateAPIView):
    queryset = Lead.objects.all()
    serializer_class = LeadConvertSerializer
    permission_classes = [permissions.IsAuthenticated]

    def update(self, request, *args, **kwargs):
        lead = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Create customer
        customer = Customer.objects.create(
            name=serializer.validated_data['customer_name'],
            email=lead.email,
            phone=lead.phone,
            address='',
            company=lead.company
        )

        # Create opportunity
        opportunity = Opportunity.objects.create(
            customer=customer,
            title=serializer.validated_data['opportunity_title'],
            description=lead.notes,
            value=serializer.validated_data['opportunity_value'],
            status='qualified',
            expected_close_date=serializer.validated_data['expected_close_date'],
            assigned_to=lead.assigned_to,
            probability=50
        )

        # Update lead status
        lead.status = 'won'
        lead.save()

        return Response({
            'message': 'تم تحويل العميل المحتمل بنجاح',
            'customer_id': customer.id,
            'opportunity_id': opportunity.id
        })

class OpportunityListCreateView(generics.ListCreateAPIView):
    serializer_class = OpportunitySerializer
    permission_classes = [permissions.IsAuthenticated]
    search_fields = ['title', 'customer__name', 'description']
    filterset_fields = ['status']
    ordering_fields = ['expected_close_date', 'value', 'probability']

    def get_queryset(self):
        if self.request.user.role == 'admin':
            return Opportunity.objects.all()
        return Opportunity.objects.filter(assigned_to=self.request.user)

class OpportunityDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Opportunity.objects.all()
    serializer_class = OpportunitySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.role == 'admin':
            return Opportunity.objects.all()
        return Opportunity.objects.filter(assigned_to=self.request.user)

class ActivityListCreateView(generics.ListCreateAPIView):
    serializer_class = ActivitySerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['type']
    ordering_fields = ['date']

    def get_queryset(self):
        return Activity.objects.filter(created_by=self.request.user)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

class ActivityDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Activity.objects.all()
    serializer_class = ActivitySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Activity.objects.filter(created_by=self.request.user)

class LeadActivityListView(generics.ListAPIView):
    serializer_class = ActivitySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        lead_id = self.kwargs.get('lead_id')
        return Activity.objects.filter(lead_id=lead_id)

class OpportunityActivityListView(generics.ListAPIView):
    serializer_class = ActivitySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        opportunity_id = self.kwargs.get('opportunity_id')
        return Activity.objects.filter(opportunity_id=opportunity_id)

class CRMDashboardView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        today = timezone.now().date()
        thirty_days_ago = today - timedelta(days=30)

        lead_query = Lead.objects.filter(assigned_to=user)
        opportunity_query = Opportunity.objects.filter(assigned_to=user)

        stats = {
            'leads_summary': {
                'total': lead_query.count(),
                'new_last_30_days': lead_query.filter(created_at__gte=thirty_days_ago).count(),
                'by_status': {
                    status: lead_query.filter(status=status).count()
                    for status, _ in Lead.STATUS_CHOICES
                },
                'by_source': {
                    source: lead_query.filter(source=source).count()
                    for source, _ in Lead.SOURCE_CHOICES
                }
            },
            'opportunities_summary': {
                'total': opportunity_query.count(),
                'total_value': opportunity_query.aggregate(total=Sum('value'))['total'],
                'by_status': {
                    status: opportunity_query.filter(status=status).count()
                    for status, _ in Opportunity.STATUS_CHOICES
                },
                'closing_this_month': opportunity_query.filter(
                    expected_close_date__year=today.year,
                    expected_close_date__month=today.month
                ).count()
            },
            'activities_summary': {
                'total': Activity.objects.filter(created_by=user).count(),
                'today': Activity.objects.filter(created_by=user, date=today).count(),
                'by_type': {
                    type_: Activity.objects.filter(created_by=user, type=type_).count()
                    for type_, _ in Activity.TYPE_CHOICES
                }
            }
        }
        
        return Response(stats)

class CRMReportView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        start_date = request.query_params.get('start_date', None)
        end_date = request.query_params.get('end_date', None)
        
        lead_query = Lead.objects.all()
        opportunity_query = Opportunity.objects.all()
        
        if request.user.role != 'admin':
            lead_query = lead_query.filter(assigned_to=request.user)
            opportunity_query = opportunity_query.filter(assigned_to=request.user)
            
        if start_date:
            lead_query = lead_query.filter(created_at__date__gte=start_date)
            opportunity_query = opportunity_query.filter(created_at__date__gte=start_date)
        if end_date:
            lead_query = lead_query.filter(created_at__date__lte=end_date)
            opportunity_query = opportunity_query.filter(created_at__date__lte=end_date)

        report = {
            'leads_analysis': {
                'total_leads': lead_query.count(),
                'conversion_rate': lead_query.filter(status='won').count() / lead_query.count() if lead_query.count() > 0 else 0,
                'by_source': lead_query.values('source').annotate(
                    count=Count('id'),
                    conversion_rate=Count('id', filter=Q(status='won')) * 1.0 / Count('id')
                )
            },
            'opportunities_analysis': {
                'total_opportunities': opportunity_query.count(),
                'total_value': opportunity_query.aggregate(total=Sum('value'))['total'],
                'win_rate': opportunity_query.filter(status='closed_won').count() / opportunity_query.count() if opportunity_query.count() > 0 else 0,
                'by_status': opportunity_query.values('status').annotate(
                    count=Count('id'),
                    total_value=Sum('value')
                )
            }
        }
        
        return Response(report)

class CRMAnalyticsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        period = request.query_params.get('period', '30')
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=int(period))

        leads_query = Lead.objects.filter(created_at__date__range=[start_date, end_date])
        opportunities_query = Opportunity.objects.filter(created_at__date__range=[start_date, end_date])
        
        if request.user.role != 'admin':
            leads_query = leads_query.filter(assigned_to=request.user)
            opportunities_query = opportunities_query.filter(assigned_to=request.user)

        analytics = {
            'lead_metrics': {
                'total_leads': leads_query.count(),
                'by_status': leads_query.values('status').annotate(count=Count('id')),
                'by_source': leads_query.values('source').annotate(count=Count('id')),
                'conversion_rate': calculate_lead_conversion_rate(leads_query),
                'average_qualification_time': calculate_avg_qualification_time(leads_query)
            },
            'opportunity_metrics': {
                'total_opportunities': opportunities_query.count(),
                'total_value': opportunities_query.aggregate(total=Sum('value'))['total'] or 0,
                'by_status': opportunities_query.values('status').annotate(
                    count=Count('id'),
                    value=Sum('value')
                ),
                'win_rate': calculate_opportunity_win_rate(opportunities_query),
                'average_deal_size': calculate_average_deal_size(opportunities_query)
            },
            'activity_metrics': calculate_activity_metrics(request.user, start_date, end_date),
            'sales_pipeline': calculate_sales_pipeline(opportunities_query)
        }
        
        return Response(analytics)

class SalesFunnelView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        period = request.query_params.get('period', '90')
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=int(period))

        funnel_data = {
            'leads': Lead.objects.filter(
                created_at__date__range=[start_date, end_date]
            ).count(),
            'qualified_leads': Lead.objects.filter(
                created_at__date__range=[start_date, end_date],
                status='qualified'
            ).count(),
            'opportunities': Opportunity.objects.filter(
                created_at__date__range=[start_date, end_date]
            ).count(),
            'proposals': Opportunity.objects.filter(
                created_at__date__range=[start_date, end_date],
                status='proposal'
            ).count(),
            'negotiations': Opportunity.objects.filter(
                created_at__date__range=[start_date, end_date],
                status='negotiation'
            ).count(),
            'won_deals': Opportunity.objects.filter(
                created_at__date__range=[start_date, end_date],
                status='closed_won'
            ).count()
        }

        conversion_rates = calculate_funnel_conversion_rates(funnel_data)
        
        return Response({
            'funnel_stages': funnel_data,
            'conversion_rates': conversion_rates,
            'average_cycle_time': calculate_average_sales_cycle(start_date, end_date)
        })

class LeadSourceAnalysisView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        period = request.query_params.get('period', '180')
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=int(period))

        leads = Lead.objects.filter(created_at__date__range=[start_date, end_date])
        
        source_analysis = leads.values('source').annotate(
            total_leads=Count('id'),
            qualified_leads=Count('id', filter=Q(status='qualified')),
            converted_leads=Count('id', filter=Q(status='won')),
            conversion_rate=Count('id', filter=Q(status='won')) * 100.0 / Count('id'),
            average_qualification_time=Avg(
                F('qualified_date') - F('created_at'),
                filter=Q(qualified_date__isnull=False)
            )
        )

        return Response({
            'source_performance': source_analysis,
            'best_performing_sources': identify_best_sources(source_analysis),
            'trend_analysis': analyze_source_trends(leads, start_date, end_date)
        })

class DummyAPIView(APIView):
    def get(self, request, *args, **kwargs):
        return Response({"message": "CRM API"})

urlpatterns = []

def calculate_lead_conversion_rate(leads):
    total_leads = leads.count()
    if total_leads == 0:
        return 0
    converted_leads = leads.filter(status='won').count()
    return (converted_leads / total_leads) * 100

def calculate_avg_qualification_time(leads):
    qualified_leads = leads.filter(
        qualified_date__isnull=False
    ).aggregate(
        avg_time=Avg(F('qualified_date') - F('created_at'))
    )
    return qualified_leads['avg_time'].days if qualified_leads['avg_time'] else 0

def calculate_opportunity_win_rate(opportunities):
    total = opportunities.count()
    if total == 0:
        return 0
    won = opportunities.filter(status='closed_won').count()
    return (won / total) * 100

def calculate_average_deal_size(opportunities):
    won_deals = opportunities.filter(status='closed_won')
    total_value = won_deals.aggregate(total=Sum('value'))['total'] or 0
    count = won_deals.count()
    return total_value / count if count > 0 else 0

def calculate_activity_metrics(user, start_date, end_date):
    activities = Activity.objects.filter(
        created_at__date__range=[start_date, end_date]
    )
    if user.role != 'admin':
        activities = activities.filter(created_by=user)

    return {
        'total_activities': activities.count(),
        'by_type': activities.values('type').annotate(count=Count('id')),
        'completion_rate': calculate_activity_completion_rate(activities),
        'daily_activity': activities.values('date').annotate(count=Count('id'))
    }

def calculate_sales_pipeline(opportunities):
    return opportunities.values('status').annotate(
        count=Count('id'),
        value=Sum('value')
    ).order_by('status')

def calculate_funnel_conversion_rates(funnel_data):
    conversion_rates = {}
    stages = list(funnel_data.items())
    
    for i in range(len(stages) - 1):
        current_stage, current_count = stages[i]
        next_stage, next_count = stages[i + 1]
        
        if current_count > 0:
            conversion_rate = (next_count / current_count) * 100
        else:
            conversion_rate = 0
            
        conversion_rates[f'{current_stage}_to_{next_stage}'] = conversion_rate
        
    return conversion_rates

def calculate_average_sales_cycle(start_date, end_date):
    won_opportunities = Opportunity.objects.filter(
        created_at__date__range=[start_date, end_date],
        status='closed_won',
        closed_date__isnull=False
    )
    
    cycle_times = won_opportunities.aggregate(
        avg_cycle=Avg(F('closed_date') - F('created_at'))
    )
    
    return cycle_times['avg_cycle'].days if cycle_times['avg_cycle'] else 0

def identify_best_sources(source_analysis):
    return sorted(
        source_analysis,
        key=lambda x: (x['conversion_rate'], x['total_leads']),
        reverse=True
    )[:5]

def analyze_source_trends(leads, start_date, end_date):
    months = (end_date.year - start_date.year) * 12 + end_date.month - start_date.month
    trends = []
    
    for i in range(months + 1):
        month_date = (start_date.replace(day=1) + timedelta(days=32 * i)).replace(day=1)
        month_leads = leads.filter(
            created_at__year=month_date.year,
            created_at__month=month_date.month
        )
        
        trends.append({
            'month': month_date.strftime('%Y-%m'),
            'by_source': month_leads.values('source').annotate(
                count=Count('id'),
                conversion_rate=Count('id', filter=Q(status='won')) * 100.0 / Count('id')
            )
        })
    
    return trends
