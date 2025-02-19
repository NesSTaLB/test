from rest_framework import serializers
from .models import Lead, Opportunity, Activity
from users.serializers import UserSerializer
from sales.serializers import CustomerSerializer

class ActivitySerializer(serializers.ModelSerializer):
    created_by_details = UserSerializer(source='created_by', read_only=True)
    
    class Meta:
        model = Activity
        fields = ('id', 'lead', 'opportunity', 'type', 'subject', 'description',
                 'date', 'created_by', 'created_by_details', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')

class LeadSerializer(serializers.ModelSerializer):
    assigned_to_details = UserSerializer(source='assigned_to', read_only=True)
    activities = ActivitySerializer(many=True, read_only=True)
    
    class Meta:
        model = Lead
        fields = ('id', 'name', 'company', 'email', 'phone', 'source', 'status',
                 'assigned_to', 'assigned_to_details', 'notes', 'activities',
                 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')

class OpportunitySerializer(serializers.ModelSerializer):
    assigned_to_details = UserSerializer(source='assigned_to', read_only=True)
    customer_details = CustomerSerializer(source='customer', read_only=True)
    activities = ActivitySerializer(many=True, read_only=True)
    
    class Meta:
        model = Opportunity
        fields = ('id', 'customer', 'customer_details', 'title', 'description',
                 'value', 'status', 'expected_close_date', 'assigned_to',
                 'assigned_to_details', 'probability', 'notes', 'activities',
                 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')

class LeadConvertSerializer(serializers.Serializer):
    customer_name = serializers.CharField(required=True)
    opportunity_title = serializers.CharField(required=True)
    opportunity_value = serializers.DecimalField(max_digits=10, decimal_places=2, required=True)
    expected_close_date = serializers.DateField(required=True)