from django.db import models
from django.contrib.auth.models import BaseUserManager,AbstractUser,Permission
from django.contrib.auth.models import Group

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
    def create_user(self, PhoneNumber, password=None, **extra_fields):
        if not PhoneNumber:
            raise ValueError("The PhoneNumber must be set")
        user = self.model(PhoneNumber=PhoneNumber, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, PhoneNumber, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(PhoneNumber, password, **extra_fields)

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    PhoneNumber = models.CharField(max_length=15, unique=True)
    role = models.ForeignKey(Role, on_delete=models.PROTECT,)

    objects = CustomUserManager()

    USERNAME_FIELD = 'PhoneNumber'
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.PhoneNumber







