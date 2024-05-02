from django.contrib import admin

from .models import Role,CustomUser

# Register your models here.
admin.site.register(Role)
admin.site.register(CustomUser)