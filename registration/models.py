# registration/models.py
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.conf import settings

class Role(models.Model):
    ADMIN = 'admin'
    MANAGER = 'manager'
    CASHIER = 'cashier'
    STOREKEEPER = 'storekeeper'
    INVENTORY_MANAGER = 'inventory_manager'
    
    ROLE_CHOICES = [
        (ADMIN, 'Admin'),
        (MANAGER, 'Manager'),
        (CASHIER, 'Cashier'),
        (STOREKEEPER, 'Storekeeper'),
        (INVENTORY_MANAGER, 'Inventory Manager'),
    ]
    
    name = models.CharField(max_length=100, choices=ROLE_CHOICES, default=ADMIN)
    
    def __str__(self):
        return self.get_name_display()

class CustomUserManager(BaseUserManager):
    def create_user(self, phone_number, password=None, **extra_fields):
        if not phone_number:
            raise ValueError('The Phone Number field must be set')
        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(phone_number, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    
    phone_number = models.CharField(max_length=20, blank=True, null=True, unique=True)
    role = models.ForeignKey(Role, on_delete=models.PROTECT, null=True, default=1)
    username = models.CharField(max_length=150, unique=True, null=True)
    is_staff = models.BooleanField(default=False)
    id = models.AutoField(primary_key=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.phone_number


class Business(models.Model):
    business_name = models.CharField(max_length=255)
    business_address = models.CharField(max_length=255)
    business_phone_number = models.CharField(max_length=20, null=True, blank=True)
    lipa_number = models.CharField(max_length=15, blank=True, null=True)
    business_type = models.CharField(max_length=100, blank=True, null=True)
    phone_network = models.CharField(max_length=10, null=True, blank=True)
    owner = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    id = models.AutoField(primary_key=True)
    has_benefited_from_offer = models.BooleanField(default=False)

    def __str__(self):
        return self.business_name
        
