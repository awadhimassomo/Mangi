from django.db import models
from django.contrib.auth.models import BaseUserManager,AbstractUser,Permission
from django.contrib.auth.models import Group



class  CustomUserManager(BaseUserManager):
    """Creating a cusotmer user model"""

    def create_user(self,PhoneNumber,password=None , **extra_fields):
        if not PhoneNumber:
            raise ValueError(("The Phone must not be empty"))
        user = self.model(PhoneNumber=PhoneNumber,**extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self,PhoneNumber,password=None,**extra_fields):
        extra_fields.setdefault('is_staff',True)
        extra_fields.setdefault('is_superuser',True)
        return
        self.create_user(
            PhoneNumber,password,**extra_fields)
    
class CustomUser(AbstractUser):
    email=models.EmailField(unique=True)
    PhoneNumber=models.CharField(max_length=15,unique=True)
    first_name = models.CharField(max_length=30)
    is_staff=models.BooleanField(('staff status'),default=False,help_text=('Designates whether the user can log into this admin site'))
    is_customer=models.BooleanField(('customer status'),default=False)


    object =CustomUserManager()

    USERNAME_FIELD="phoneNumber"
    REQUIRED_FIELD =["email","first_name"]

    groups=models.ManyToManyField(Group,blank=True,related_name='customer_set')
    user_permissions=models.ManyToManyField(Permission,blank=True,related_name='customer_set')

    def __str__(Self):
        return self.phoneNumber



