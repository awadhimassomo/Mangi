from django.contrib import admin

# Register your models here.

from .models import Category, Expense, Installment, PublicProduct, Sales,Supplier,Product,Transaction,Warehouse,Purchase


admin.site.register(Category)
admin.site.register(Supplier)
admin.site.register(Product)
admin.site.register(Transaction)
admin.site.register(Warehouse)
admin.site.register(Purchase)
admin.site.register(Installment)
admin.site.register(Sales)
admin.site.register(Expense)
admin.site.register(PublicProduct)


