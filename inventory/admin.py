from django.contrib import admin

# Register your models here.

from .models import BusinessType, Category, Expense, Installment, Order, PublicProduct, Sales, SalesItem,Supplier,Product,Transaction,Warehouse,Purchase

class TransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'transaction_type', 'transaction_date', 'business_id', 'customer', 'total_amount', 'outstanding_amount')
    
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'id','product_name', 'price', 'quantity', 'barcode', 'date_created',
        'supplier', 'category', 'warehouse', 'expire_date', 'active', 'isDeleted'
    )
    search_fields = ('product_name', 'barcode', 'supplier__name', 'category__name')
    list_filter = ('category', 'active', 'warehouse', 'isDeleted', 'isSynced')
    readonly_fields = ('date_created', 'date_updated', 'lastSyncTime')
    fieldsets = (
        (None, {
            'fields': (
                'product_name', 'price', 'cost', 'quantity', 'barcode', 'supplier',
                'category', 'warehouse', 'expire_date', 'image'
            )
        }),
        ('Stock Details', {
            'fields': ('min_stock', 'max_stock', 'location_type', 'location_identifier')
        }),
        ('Status and Sync', {
            'fields': ('active', 'isDeleted', 'isSynced', 'lastSyncTime'),
        }),
        ('Dates', {
            'fields': ('date_created', 'date_updated'),
        }),
    )
    
@admin.register(Sales)
class SalesAdmin(admin.ModelAdmin):
    list_display = ('id', 'transaction_id', 'business_id', 'total_amount', 'isSynced', 'isDeleted')
    list_filter = ('isSynced', 'isDeleted', 'business_id')
    search_fields = ('transaction_id__id', 'business__name')

admin.site.register(Product, ProductAdmin)   
admin.site.register(Category)
admin.site.register(Supplier)
admin.site.register(Transaction, TransactionAdmin)
admin.site.register(Warehouse)
admin.site.register(Purchase)
admin.site.register(Installment)
admin.site.register(Expense)
admin.site.register(PublicProduct)
admin.site.register(Order)
admin.site.register(BusinessType)
admin.site.register(SalesItem)





