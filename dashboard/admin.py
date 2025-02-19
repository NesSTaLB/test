from django.contrib import admin
from .models import DashboardWidget, UserDashboardPreference, UserWidgetSettings

@admin.register(DashboardWidget)
class DashboardWidgetAdmin(admin.ModelAdmin):
    list_display = ('title', 'widget_type', 'position', 'is_active', 'refresh_interval')
    list_filter = ('widget_type', 'is_active')
    search_fields = ('title',)
    ordering = ('position',)

@admin.register(UserDashboardPreference)
class UserDashboardPreferenceAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'updated_at')
    search_fields = ('user__username',)
    readonly_fields = ('created_at', 'updated_at')

@admin.register(UserWidgetSettings)
class UserWidgetSettingsAdmin(admin.ModelAdmin):
    list_display = ('user_preference', 'widget', 'position', 'is_visible')
    list_filter = ('is_visible',)
    search_fields = ('user_preference__user__username', 'widget__title')
    ordering = ('user_preference', 'position')
