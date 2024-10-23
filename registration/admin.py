from django.contrib import admin

from .models import Address, Role,CustomUser,Business,Customer

# Register your models here.
admin.site.register(Role)
admin.site.register(CustomUser)
admin.site.register(Business)
admin.site.register(Customer)
admin.site.register(Address)
