from django.urls import path
from . import views

app_name = 'project_management'

urlpatterns = [
    path('', views.ProjectListCreateView.as_view(), name='project-list'),
    path('<int:pk>/', views.ProjectDetailView.as_view(), name='project-detail'),
    path('<int:project_id>/tasks/', views.TaskListCreateView.as_view(), name='task-list'),
    path('tasks/<int:pk>/', views.TaskDetailView.as_view(), name='task-detail'),
    path('tasks/assigned/', views.AssignedTasksView.as_view(), name='assigned-tasks'),
    path('dashboard/', views.ProjectDashboardView.as_view(), name='dashboard'),
    path('reports/', views.ProjectReportsView.as_view(), name='reports'),
    path('<int:project_id>/timeline/', views.ProjectTimelineView.as_view(), name='timeline'),
    path('team-performance/', views.TeamPerformanceView.as_view(), name='team-performance'),
]