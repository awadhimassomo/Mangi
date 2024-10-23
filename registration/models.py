# registration/models.py
from venv import logger
from django.apps import apps
from django.db import models
from rest_framework import viewsets, status
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.conf import settings
import qrcode
import json
import logging
import uuid
from django.forms import ValidationError
from io import BytesIO
from django.core.files import File
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import MinValueValidator
from django.core.validators import MaxValueValidator


from inventory.models import Transaction



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
    def create_user(self, phoneNumber, password=None, **extra_fields):
        if not phoneNumber:
            raise ValueError('The Phone Number field must be set')

       

        user = self.model(phoneNumber=phoneNumber, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phoneNumber, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields['isVerified'] = True  # Superusers are always verified
        return self.create_user(phoneNumber, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    phoneNumber = models.CharField(max_length=20, blank=True, null=True, unique=True)
    email = models.EmailField(blank=True, null=True)
    role = models.ForeignKey('Role', on_delete=models.PROTECT, null=True)
    username = models.CharField(max_length=150, unique=False, null=True)
    is_staff = models.BooleanField(default=False)
    id = models.AutoField(primary_key=True)
    vcard_qrImage = models.ImageField(upload_to='vcards/', blank=True, null=True)
    isVerified = models.BooleanField(default=False)  # New field to check if the user is verified

    objects = CustomUserManager()

    USERNAME_FIELD = 'phoneNumber'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.phoneNumber or 'Unnamed User'

    def generate_vcard(self):
        vcard = f"""
BEGIN:VCARD
VERSION:3.0
FN:{self.username or ''}
TEL:{self.phoneNumber or ''}
EMAIL:{self.email or ''}
END:VCARD
"""
        return vcard

    def generate_vcard_qr_code(self):
        vcard = self.generate_vcard()
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(vcard)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Use phone number as the file name
        temp_name = f"vcard-{self.phoneNumber}.png"
        buffer = BytesIO()
        img.save(buffer, 'PNG')
        logger.info(f"vCard QR code generated, saving to {temp_name}")

        self.vcard_qrImage.save(temp_name, File(buffer), save=False)
        buffer.close()
        logger.info(f"vCard QR code saved to {self.vcard_qrImage.path}")

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.vcard_qrImage:
            logger.info("No vCard QR code found, generating new one.")
            self.generate_vcard_qr_code()
        else:
            logger.info("vCard QR code already exists, skipping generation.")

    def list_businesses(self):
        return self.businesses.all()

class BusinessManager(models.Manager):
    def import_public_products(self, business_uuid):
        Business = apps.get_model('registration', 'Business')
        business = Business.objects.get(uuid=business_uuid)

        PublicProduct = apps.get_model('inventory', 'PublicProduct')
        Product = apps.get_model('inventory', 'Product')
        Category = apps.get_model('inventory', 'Category')
        Supplier = apps.get_model('inventory', 'Supplier')
        Warehouse = apps.get_model('inventory', 'Warehouse')

        default_category = Category.objects.first()
        default_supplier = Supplier.objects.first()
        default_warehouse = Warehouse.objects.first()

        public_products = PublicProduct.objects.filter(businessType=business.businessType)

        with transaction.atomic():
            for public_product in public_products:
                category = getattr(public_product, 'category', default_category)
                supplier = getattr(public_product, 'supplier', default_supplier)
                warehouse = getattr(public_product, 'warehouse', default_warehouse)

                if category is None or supplier is None or warehouse is None:
                    logger.warning(f"Skipping product creation for {public_product.product_name} due to missing fields.")
                    continue

                logger.info(f"Creating product: {public_product.product_name} for business: {business.businessName}")

                Product.objects.create(
                    business=business,
                    product_name=public_product.product_name or "Unnamed Product",
                    barcode=public_product.barcode,
                    description=public_product.description,
                    price=0.0,
                    cost=0.0,
                    quantity=0,
                    supplier=supplier,
                    category=category,
                    warehouse=warehouse,
                    expire_date=None,
                    active=True,
                    taxable=True,
                    product_type=None,
                    discountable=True,
                    image=None,
                    min_stock=20,
                    max_stock=None,
                    location_type='store',
                    location_identifier=None,
                )

        logger.info(f"Finished importing products for business: {business.businessName}")
        return f"Imported {len(public_products)} products for business: {business.businessName}"
    


class Business(models.Model):
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    businessName = models.CharField(max_length=255)
    businessAddress = models.CharField(max_length=255)
    businessPhoneNumber = models.CharField(max_length=20, null=True, blank=True)
    lipaNumber = models.CharField(max_length=15, blank=True, null=True)
    phoneNetwork = models.CharField(max_length=10, null=True, blank=True)
    website = models.URLField(blank=True, null=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    qrImage = models.ImageField(upload_to='qr_codes/', blank=True, null=True)
    isSynced = models.BooleanField(default=False)
    lastSyncTime = models.DateTimeField(default=timezone.now)
    isDeleted = models.BooleanField(default=False)
    hasBenefitedFromOffer = models.BooleanField(default=False)

    # Establishing a relationship with BusinessType
    businessType = models.ForeignKey('inventory.BusinessType', on_delete=models.SET_NULL, null=True, blank=True)

    objects = BusinessManager()

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)

        if not self.qrImage:
            self.generate_qr_code()

        if is_new:
            print(f"New business created: {self.businessName}, triggering predefined data insertion.")
            Business.objects.import_public_products(self.uuid)  # Trigger predefined data insertion

    def generate_qr_code(self):
        vcard = f"""
BEGIN:VCARD
VERSION:3.0
FN:{self.businessName}
ORG:{self.businessName}
TEL:{self.businessPhoneNumber}
ADR;TYPE=WORK,PREF:;;{self.businessAddress};;;
URL:{self.website}
END:VCARD
"""
        print(f"Generating QR code for vCard:\n{vcard}")

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(vcard)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        temp_name = f"qr-{self.pk}.png"
        buffer = BytesIO()
        img.save(buffer, 'PNG')
        print(f"QR code generated, saving to {temp_name}")

        self.qrImage.save(temp_name, File(buffer), save=False)
        buffer.close()
        super().save(update_fields=['qrImage'])

        qr_code_path = self.qrImage.path
        print(f"QR code file saved at: {qr_code_path}")

    def __str__(self):
        return self.businessName if self.businessName else 'Unnamed Business'

class BusinessProfile(models.Model):
    business = models.OneToOneField('Business', on_delete=models.CASCADE, related_name='profile')
    tinNumber = models.CharField(max_length=20, blank=True, null=True)  # TIN number
    businessLicenseNumber = models.CharField(max_length=50, blank=True, null=True)  # License number
    licenseApplicationDate = models.DateField(null=True, blank=True)  # Date for license application
    businessEmail = models.EmailField(blank=True, null=True)  # Business email address
    contactPerson = models.CharField(max_length=255, blank=True, null=True)  # Contact person
    logo = models.ImageField(upload_to='business_logos/', null=True, blank=True)  # Logo image field

    def __str__(self):
        return f"Profile of {self.business.businessName}"


# Address model
class Address(models.Model):
    street_address = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True, validators=[
        MinValueValidator(-90),
        MaxValueValidator(90)
    ])
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True, validators=[
        MinValueValidator(-180),
        MaxValueValidator(180)
    ])

    def __str__(self):
        return f"{self.street_address}, {self.city}, {self.state}, {self.postal_code}, {self.country}"
    

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True)

    def __str__(self):
        return f"{self.user.phoneNumber}'s Profile"

# Signal for creating profile when user is created
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

# Signal for saving profile when user is saved
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def save_user_profile(sender, instance, **kwargs):
    # Ensure the profile exists before trying to save
    if hasattr(instance, 'profile'):
        instance.profile.save()
    
class Customer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    phoneNumber = models.CharField(max_length=20, unique=True)
    tinNumber = models.CharField(max_length=100, null=True, blank=True)  # Added TIN number field
    date_added = models.DateTimeField(auto_now_add=True)
    business = models.ForeignKey('registration.Business', on_delete=models.CASCADE)
    frequency = models.IntegerField(default=1)  # Field to track frequency
    isSynced = models.BooleanField(default=False)  # Field to track synchronization status
    isDeleted = models.BooleanField(default=False)  # Field to track if the customer is deleted

    def __str__(self):
        return self.name
    
class Partner(models.Model):
    # Basic Partner Information
    name = models.CharField(max_length=255, unique=True)
    contact_person = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    phone = models.CharField(max_length=15, null=True, blank=True)

    # Address Information
    address = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    postal_code = models.CharField(max_length=20, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)

    # Ownership Percentage
    ownership_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    # Secondary Data Fields for future relationships (e.g., transactions)
    business_id = models.IntegerField(null=True, blank=True)  # Secondary reference to another system

    # View count (for tracking in the mobile app)
    views = models.IntegerField(default=0)

    # Boolean flags
    receive_sms = models.BooleanField(default=False)  # Whether the partner allows receiving SMS notifications
    receive_email_reports = models.BooleanField(default=False)  # Whether the partner wants reports via email

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
