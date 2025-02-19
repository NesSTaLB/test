from django.shortcuts import render
from rest_framework import generics, permissions, status, filters
from rest_framework.response import Response
from django.db.models import Q
from .models import Project, Task
from .serializers import ProjectSerializer, TaskSerializer
from rest_framework.views import APIView
from django.db.models import Count, Sum, Q
from django.utils import timezone
from datetime import timedelta
from .utils import (
    calculate_project_progress,
    get_overdue_tasks,
    calculate_team_workload
)
from django_filters.rest_framework import DjangoFilterBackend

class ProjectListCreateView(generics.ListCreateAPIView):
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'manager']
    search_fields = ['name', 'description']
    ordering_fields = ['created_at', 'start_date', 'end_date']

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Project.objects.all()
        return Project.objects.filter(
            Q(manager=user) | Q(team_members=user)
        ).distinct()

class ProjectDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Project.objects.all()
        return Project.objects.filter(
            Q(manager=user) | Q(team_members=user)
        ).distinct()

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = serializer.data
        data['progress'] = calculate_project_progress(instance)
        return Response(data)

class TaskListCreateView(generics.ListCreateAPIView):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'priority', 'assigned_to']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'due_date', 'priority']

    def get_queryset(self):
        project_id = self.kwargs.get('project_id')
        return Task.objects.filter(project_id=project_id)

    def perform_create(self, serializer):
        project_id = self.kwargs.get('project_id')
        serializer.save(project_id=project_id)

class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

class AssignedTasksView(generics.ListAPIView):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'priority', 'project']
    search_fields = ['title', 'description', 'project__name']
    ordering_fields = ['created_at', 'due_date', 'priority']

    def get_queryset(self):
        return Task.objects.filter(assigned_to=self.request.user)

class ProjectDashboardView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        if user.role == 'admin':
            projects = Project.objects.all()
        else:
            projects = Project.objects.filter(
                Q(manager=user) | Q(team_members=user)
            ).distinct()

        stats = {
            'total_projects': projects.count(),
            'projects_by_status': {
                status: projects.filter(status=status).count()
                for status, _ in Project.STATUS_CHOICES
            },
            'my_assigned_tasks': Task.objects.filter(assigned_to=user).count(),
            'overdue_tasks': Task.objects.filter(
                assigned_to=user,
                due_date__lt=timezone.now().date(),
                status__in=['todo', 'in_progress']
            ).count()
        }
        
        return Response(stats)

class ProjectReportsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        projects_query = Project.objects.all()
        if start_date:
            projects_query = projects_query.filter(start_date__gte=start_date)
        if end_date:
            projects_query = projects_query.filter(end_date__lte=end_date)

        if not request.user.role == 'admin':
            projects_query = projects_query.filter(
                Q(manager=request.user) | Q(team_members=request.user)
            ).distinct()

        reports = {
            'projects_summary': {
                'total_projects': projects_query.count(),
                'by_status': projects_query.values('status').annotate(
                    count=Count('id')
                ),
                'by_completion': {
                    'completed': projects_query.filter(status='completed').count(),
                    'in_progress': projects_query.filter(status='in_progress').count(),
                    'delayed': projects_query.filter(
                        end_date__lt=timezone.now().date(),
                        status__in=['new', 'in_progress']
                    ).count()
                }
            },
            'tasks_summary': {
                'total_tasks': Task.objects.filter(project__in=projects_query).count(),
                'by_status': Task.objects.filter(project__in=projects_query).values(
                    'status'
                ).annotate(count=Count('id')),
                'by_priority': Task.objects.filter(project__in=projects_query).values(
                    'priority'
                ).annotate(count=Count('id')),
                'overdue_tasks': get_overdue_tasks().filter(
                    project__in=projects_query
                ).count()
            },
            'team_performance': {
                'workload': calculate_team_workload(
                    User.objects.filter(
                        Q(managed_projects__in=projects_query) |
                        Q(project_teams__in=projects_query)
                    ).distinct()
                )
            },
            'project_progress': {
                project.id: calculate_project_progress(project)
                for project in projects_query
            }
        }
        
        return Response(reports)

class ProjectTimelineView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, project_id):
        try:
            project = Project.objects.get(id=project_id)
            if not request.user.role == 'admin' and request.user != project.manager:
                return Response(
                    {'error': 'ليس لديك صلاحية لعرض هذا المشروع'},
                    status=403
                )

            timeline = {
                'project_info': {
                    'name': project.name,
                    'start_date': project.start_date,
                    'end_date': project.end_date,
                    'status': project.status,
                    'progress': calculate_project_progress(project)
                },
                'tasks_timeline': Task.objects.filter(project=project).values(
                    'id', 'title', 'status', 'start_date', 'due_date',
                    'assigned_to__username', 'priority'
                ).order_by('start_date')
            }
            
            return Response(timeline)
            
        except Project.DoesNotExist:
            return Response(
                {'error': 'المشروع غير موجود'},
                status=404
            )

class TeamPerformanceView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        team_members = request.query_params.getlist('team_members')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        tasks_query = Task.objects.all()
        if team_members:
            tasks_query = tasks_query.filter(assigned_to__id__in=team_members)
        if start_date:
            tasks_query = tasks_query.filter(start_date__gte=start_date)
        if end_date:
            tasks_query = tasks_query.filter(due_date__lte=end_date)

        performance = {
            'team_overview': {
                'total_tasks': tasks_query.count(),
                'completed_tasks': tasks_query.filter(status='completed').count(),
                'overdue_tasks': tasks_query.filter(
                    due_date__lt=timezone.now().date(),
                    status__in=['todo', 'in_progress']
                ).count()
            },
            'individual_performance': tasks_query.values(
                'assigned_to__username'
            ).annotate(
                total_tasks=Count('id'),
                completed_tasks=Count('id', filter=Q(status='completed')),
                overdue_tasks=Count(
                    'id',
                    filter=Q(
                        due_date__lt=timezone.now().date(),
                        status__in=['todo', 'in_progress']
                    )
                )
            ),
            'productivity_metrics': {
                'average_completion_time': calculate_average_completion_time(tasks_query),
                'task_completion_rate': calculate_task_completion_rate(tasks_query)
            }
        }
        
        return Response(performance)

def calculate_average_completion_time(tasks):
    completed_tasks = tasks.filter(status='completed')
    if not completed_tasks.exists():
        return 0
    
    total_days = 0
    for task in completed_tasks:
        if task.completed_at and task.start_date:
            days = (task.completed_at.date() - task.start_date).days
            total_days += max(0, days)
    
    return total_days / completed_tasks.count()

def calculate_task_completion_rate(tasks):
    if not tasks.exists():
        return 0
    
    completed = tasks.filter(status='completed').count()
    total = tasks.count()
    
    return (completed / total) * 100 if total > 0 else 0
