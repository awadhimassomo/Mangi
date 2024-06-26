from django.contrib import admin

# Register your models here.

from .models import Category,Supplier,Product,Transaction,Warehouse,Address,Purchase


admin.site.register(Category)
admin.site.register(Supplier)
admin.site.register(Product)
admin.site.register(Transaction)
admin.site.register(Warehouse)
admin.site.register(Address)
admin.site.register(Purchase)


