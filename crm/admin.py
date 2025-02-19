from django.contrib import admin
from .models import Lead, Opportunity, Activity

@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ('name', 'company', 'email', 'phone', 'source', 'status', 'assigned_to')
    list_filter = ('status', 'source', 'created_at')
    search_fields = ('name', 'company', 'email', 'phone')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Opportunity)
class OpportunityAdmin(admin.ModelAdmin):
    list_display = ('title', 'customer', 'value', 'status', 'probability', 'expected_close_date')
    list_filter = ('status', 'expected_close_date')
    search_fields = ('title', 'customer__name', 'description')
    date_hierarchy = 'expected_close_date'
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ('subject', 'type', 'date', 'lead', 'opportunity', 'created_by')
    list_filter = ('type', 'date')
    search_fields = ('subject', 'description', 'lead__name', 'opportunity__title')
    date_hierarchy = 'date'
    readonly_fields = ('created_at', 'updated_at')
