from django.contrib import admin
from .models import Customer, Product, Sale, SaleItem

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'company', 'created_at')
    search_fields = ('name', 'email', 'phone', 'company')
    list_filter = ('created_at',)
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'sku', 'price', 'stock')
    search_fields = ('name', 'sku', 'description')
    list_filter = ('created_at',)
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('معلومات المنتج', {
            'fields': (
                'name',
                'sku',
                'description',
                'price',
                'stock',
            )
        }),
        ('الصورة', {
            'fields': ('image',),
        }),
        ('معلومات إضافية', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    class Media:
        css = {
            'all': ('css/admin_custom.css',)
        }

class SaleItemInline(admin.TabularInline):
    model = SaleItem
    extra = 1
    readonly_fields = ('total_price',)

@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'sales_person', 'date', 'status', 'total_amount')
    list_filter = ('status', 'date')
    search_fields = ('customer__name', 'sales_person__username')
    date_hierarchy = 'date'
    readonly_fields = ('created_at', 'updated_at')
    inlines = [SaleItemInline]
