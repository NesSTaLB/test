from rest_framework import serializers
from .models import Customer, Product, Sale, SaleItem
from users.serializers import UserSerializer

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ('id', 'name', 'email', 'phone', 'address', 'company', 
                 'notes', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ('id', 'name', 'description', 'price', 'sku', 'stock', 
                 'image', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')

class SaleItemSerializer(serializers.ModelSerializer):
    product_details = ProductSerializer(source='product', read_only=True)

    class Meta:
        model = SaleItem
        fields = ('id', 'sale', 'product', 'product_details', 'quantity', 
                 'unit_price', 'total_price')
        read_only_fields = ('id', 'total_price')

class SaleSerializer(serializers.ModelSerializer):
    items = SaleItemSerializer(many=True, read_only=True)
    customer_details = CustomerSerializer(source='customer', read_only=True)
    sales_person_details = UserSerializer(source='sales_person', read_only=True)
    
    class Meta:
        model = Sale
        fields = ('id', 'customer', 'customer_details', 'sales_person', 
                 'sales_person_details', 'date', 'status', 'total_amount', 
                 'notes', 'items', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')

class SaleCreateSerializer(serializers.ModelSerializer):
    items = SaleItemSerializer(many=True)

    class Meta:
        model = Sale
        fields = ('id', 'customer', 'sales_person', 'date', 'status', 
                 'total_amount', 'notes', 'items')

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        sale = Sale.objects.create(**validated_data)
        for item_data in items_data:
            SaleItem.objects.create(sale=sale, **item_data)
        return sale