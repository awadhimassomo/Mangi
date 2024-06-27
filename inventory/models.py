from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.apps import apps


# Category model
class Category(models.Model):
    category_name = models.CharField(max_length=255)
    unit_choices = [
        ('mls', 'Milliliters'),
        ('l', 'Liters'),
        ('g', 'Grams'),
        ('kg', 'Kilograms'),
        ('doz', 'Dozens'),
        ('pcs', 'Pieces'),
        ('box', 'Boxes'),
    ]
    unit = models.CharField(max_length=3, choices=unit_choices, blank=True, null=True)
    unit_quantity = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    business = models.ForeignKey('registration.Business', on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f'{self.category_name} - {self.unit_quantity} {self.unit}' if self.unit and self.unit_quantity else self.category_name


# Warehouse model
class Warehouse(models.Model):
    warehouse_name = models.CharField(max_length=255)
    warehouse_location = models.CharField(max_length=255)
    address = models.ForeignKey('Address', on_delete=models.PROTECT, null=True, blank=True)
    business = models.ForeignKey('registration.Business', on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.warehouse_name


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


# Supplier model
class Supplier(models.Model):
    supplier_name = models.CharField(max_length=255)
    contact_person = models.CharField(max_length=255)
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=15)
    address = models.ForeignKey('Address', on_delete=models.PROTECT, null=True, blank=True)
    business = models.ForeignKey('registration.Business', on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.supplier_name


# Product model
class Product(models.Model):
    product_name = models.CharField(max_length=255, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField(null=True)
    barcode = models.CharField(max_length=255, null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    supplier = models.ForeignKey('Supplier', on_delete=models.PROTECT)
    category = models.ForeignKey('Category', on_delete=models.PROTECT)
    warehouse = models.ForeignKey('Warehouse', on_delete=models.PROTECT)
    expire_date = models.DateField(blank=True, null=True)
    active = models.BooleanField(default=True)
    description = models.TextField(blank=True, null=True)
    taxable = models.BooleanField(default=True)
    product_type = models.CharField(max_length=255, blank=True, null=True)
    discountable = models.BooleanField(default=True)
    business = models.ForeignKey('registration.Business', on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.product_name

    class Meta:
        ordering = ['-date_updated']


# Transaction model
class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('cash', 'Cash'),
        ('lipa_namba', 'Lipa Kwa Simu'),
        ('bank_transfer', 'Bank Transfer'),
        ('credit_card', 'Credit Card'),
        ('other', 'Other'),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    transaction_date = models.DateField()
    quantity_change = models.IntegerField()
    transaction_amount = models.DecimalField(max_digits=10, decimal_places=2)
    business = models.ForeignKey('registration.Business', on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f"{self.transaction_type} - {self.transaction_date}"


# Purchase model
class Purchase(models.Model):
    customer = models.ForeignKey('registration.Customer', on_delete=models.CASCADE)
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    purchase_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.customer.name} - {self.product.product_name} - {self.quantity}'
