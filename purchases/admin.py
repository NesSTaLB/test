from django.contrib import admin
from .models import Supplier, Purchase, PurchaseItem

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('name', 'company', 'email', 'phone', 'tax_number')
    search_fields = ('name', 'company', 'email', 'phone')
    list_filter = ('created_at',)
    readonly_fields = ('created_at', 'updated_at')

class PurchaseItemInline(admin.TabularInline):
    model = PurchaseItem
    extra = 1
    readonly_fields = ('total_price',)

@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = ('reference_number', 'supplier', 'purchase_date', 'status', 'total_amount')
    list_filter = ('status', 'purchase_date')
    search_fields = ('reference_number', 'supplier__name')
    date_hierarchy = 'purchase_date'
    readonly_fields = ('created_at', 'updated_at')
    inlines = [PurchaseItemInline]
