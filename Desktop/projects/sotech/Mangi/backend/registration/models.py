from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class Role(models.Model):
    ADMIN = 'admin'
    STOREKEEPER = 'storekeeper'
    CASHIER = 'cashier'

    ROLE_CHOICES = [
        (ADMIN, 'Admin'),
        (STOREKEEPER, 'Storekeeper'),
        (CASHIER, 'Cashier'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, unique=True)

    def __str__(self):
        return self.get_role_display() 

class CustomUserManager(BaseUserManager):
    def create_user(self, email, PhoneNumber, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        if not PhoneNumber:
            raise ValueError('The PhoneNumber field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, PhoneNumber=PhoneNumber, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, PhoneNumber, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, PhoneNumber, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    PhoneNumber = models.CharField(max_length=15, unique=True)
    role = models.ForeignKey(Role, on_delete=models.PROTECT, null=True)
    username = models.CharField(max_length=150, unique=True , null= True)
    is_staff = models.BooleanField(default=False) 

    objects = CustomUserManager()


    USERNAME_FIELD = 'PhoneNumber'
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.email


class Business(models.Model):
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    # Add other fields as needed


