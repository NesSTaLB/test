from django.contrib import admin
from django.utils.html import format_html
from .models import Project, Task

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_status_with_progress', 'manager', 'get_team_size', 'get_budget_display', 'start_date', 'end_date')
    list_filter = ('status', 'manager', 'start_date')
    search_fields = ('name', 'description', 'manager__username')
    filter_horizontal = ('team_members',)
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('معلومات أساسية', {
            'fields': ('name', 'description', 'manager', 'status'),
            'classes': ('wide',)
        }),
        ('تفاصيل الفريق', {
            'fields': ('team_members',),
            'classes': ('wide',)
        }),
        ('التواريخ', {
            'fields': ('start_date', 'end_date'),
            'classes': ('wide',)
        }),
        ('معلومات إضافية', {
            'fields': ('budget', 'project_plans', 'project_images'),
            'classes': ('collapse', 'wide')
        }),
    )
    
    class Media:
        css = {
            'all': ('admin/css/forms.css',)
        }
    
    @admin.display(description="الحالة والتقدم")
    def get_status_with_progress(self, obj):
        if obj.progress_percentage is None:
            return "N/A"
        progress_bar = format_html(
            '<div style="width:100px; background-color:#f1f1f1; height:20px; border-radius:10px; overflow:hidden;">'
            '<div style="width:{}%; height:100%; background-color:{}; transition: all .3s ease"></div>'
            '</div> {} ({}%)',
            obj.progress_percentage,
            '#2ecc71' if obj.status == 'completed' else '#f1c40f',
            obj.get_status_display(),
            obj.progress_percentage
        )
        return progress_bar
    
    @admin.display(description="حجم الفريق")
    def get_team_size(self, obj):
        count = obj.team_members.count()
        return format_html(
            '<span title="{}">{} {}</span>',
            ", ".join([str(member) for member in obj.team_members.all()]), 
            count,
            'عضو' if count == 1 else 'أعضاء'
        )
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['name'].widget.attrs['class'] = 'vTextField'
        form.base_fields['description'].widget.attrs['class'] = 'vLargeTextField'
        form.base_fields['budget'].widget.attrs['class'] = 'vMoneyField'
        return form

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'get_project_link', 'get_priority_with_status', 'assigned_to', 'get_due_date_status', 'get_completion_info')
    list_filter = ('status', 'priority', 'project', 'assigned_to')
    search_fields = ('title', 'description', 'project__name', 'assigned_to__username')
    date_hierarchy = 'due_date'
    
    fieldsets = (
        ('معلومات المهمة', {
            'fields': ('title', 'description', 'project'),
            'classes': ('wide',)
        }),
        ('التخصيص والحالة', {
            'fields': ('assigned_to', 'status', 'priority'),
            'classes': ('wide',)
        }),
        ('التواريخ', {
            'fields': ('start_date', 'due_date'),
            'classes': ('wide',)
        }),
        ('تتبع الوقت', {
            'fields': ('estimated_hours', 'actual_hours', 'completed_at'),
            'classes': ('collapse', 'wide')
        }),
    )
    
    readonly_fields = ('completed_at',)
    
    class Media:
        css = {
            'all': ('admin/css/forms.css',)
        }
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['title'].widget.attrs['class'] = 'vTextField'
        form.base_fields['description'].widget.attrs['class'] = 'vLargeTextField'
        return form
    
    @admin.display(description="المشروع")
    def get_project_link(self, obj):
        if not obj.project:
            return "N/A"
        return format_html(
            '<a href="{}">{}</a>',
            f'/admin/project_management/project/{obj.project.id}/change/',
            obj.project.name
        )
    
    @admin.display(description="الأولوية والحالة")
    def get_priority_with_status(self, obj):
        priority_colors = {
            'low': '#2ecc71',
            'medium': '#f1c40f',
            'high': '#e74c3c',
        }
        color = priority_colors.get(obj.priority, '#95a5a6')
        priority_badge = format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; margin-right: 5px">{}</span>',
            color,
            obj.get_priority_display()
        )
        return format_html(
            '{} | {}',
            priority_badge,
            obj.get_status_display()
        )
    
    @admin.display(description="موعد التسليم")
    def get_due_date_status(self, obj):
        style = 'color: #e74c3c;' if obj.is_overdue else ''
        return format_html(
            '<span style="{}">{} ({})</span>',
            style,
            obj.due_date if obj.due_date else "N/A",
            obj.time_remaining
        )
    
    @admin.display(description="حالة الإنجاز")
    def get_completion_info(self, obj):
        if obj.status == 'completed':
            style = 'color: #2ecc71;'
            if obj.completed_at and obj.completed_at.date() > obj.due_date:
                style = 'color: #f1c40f;'
            return format_html(
                '<span style="{}">{}</span>',
                style,
                obj.completion_status
            )
        return obj.completion_status
