from rest_framework import serializers
from .models import Supplier, Purchase, PurchaseItem
from sales.models import Product
from sales.serializers import ProductSerializer
from users.serializers import UserSerializer

class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = ('id', 'name', 'email', 'phone', 'address', 'company', 
                 'tax_number', 'notes', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')

class PurchaseItemSerializer(serializers.ModelSerializer):
    product_details = ProductSerializer(source='product', read_only=True)

    class Meta:
        model = PurchaseItem
        fields = ('id', 'purchase', 'product', 'product_details', 'quantity', 
                 'unit_price', 'total_price', 'received_quantity')
        read_only_fields = ('id', 'total_price')

class PurchaseSerializer(serializers.ModelSerializer):
    items = PurchaseItemSerializer(many=True, read_only=True)
    supplier_details = SupplierSerializer(source='supplier', read_only=True)
    created_by_details = UserSerializer(source='created_by', read_only=True)
    
    class Meta:
        model = Purchase
        fields = ('id', 'supplier', 'supplier_details', 'purchase_date', 
                 'reference_number', 'status', 'total_amount', 'tax_amount', 
                 'notes', 'created_by', 'created_by_details', 'items', 
                 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')

class PurchaseCreateSerializer(serializers.ModelSerializer):
    items = PurchaseItemSerializer(many=True)

    class Meta:
        model = Purchase
        fields = ('id', 'supplier', 'purchase_date', 'reference_number', 
                 'status', 'total_amount', 'tax_amount', 'notes', 
                 'created_by', 'items')

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        purchase = Purchase.objects.create(**validated_data)
        for item_data in items_data:
            PurchaseItem.objects.create(purchase=purchase, **item_data)
        return purchase