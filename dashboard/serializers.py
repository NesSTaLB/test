from rest_framework import serializers
from .models import DashboardWidget, UserDashboardPreference, UserWidgetSettings

class DashboardWidgetSerializer(serializers.ModelSerializer):
    class Meta:
        model = DashboardWidget
        fields = ('id', 'title', 'widget_type', 'position', 'is_active',
                 'refresh_interval', 'settings', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')

class UserWidgetSettingsSerializer(serializers.ModelSerializer):
    widget_details = DashboardWidgetSerializer(source='widget', read_only=True)

    class Meta:
        model = UserWidgetSettings
        fields = ('id', 'widget', 'widget_details', 'position', 'is_visible', 'settings')
        read_only_fields = ('id',)

class UserDashboardPreferenceSerializer(serializers.ModelSerializer):
    widgets_settings = UserWidgetSettingsSerializer(source='userwidgetsettings_set', many=True, read_only=True)

    class Meta:
        model = UserDashboardPreference
        fields = ('id', 'user', 'layout', 'widgets_settings', 'created_at', 'updated_at')
        read_only_fields = ('id', 'user', 'created_at', 'updated_at')