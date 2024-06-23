from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


#category model
class Category(models.Model):
    category_name = models.CharField(max_length=255)
    unit_choices = [
        ('mls', 'mls'),
        ('kg', 'kg'),
        ('g', 'g'),
    ]
    unit = models.CharField(max_length=3, choices=unit_choices, blank=True, null=True)
    unity_quantity = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    def __str__(self):
        return f'{self.category_name} - {self.unity_quantity} {self.unit}' if self.unit and self.unity_quantity else self.category_name

#warehouse 
class Warehouse(models.Model):
    WarehouseName = models.CharField(max_length=255)
    WarehouseLocation = models.CharField(max_length=255)
    address = models.ForeignKey('Address', on_delete=models.PROTECT, null=True, blank=True)
    def __str__(self):
        return self.WarehouseName



#Adress model
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

#Supplier Model
class Supplier(models.Model):
    supplier_name = models.CharField(max_length=255)
    contact_person = models.CharField(max_length=255)
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=15)
    address = models.ForeignKey('Address', on_delete=models.PROTECT, null=True, blank=True)
 
    

    def __str__(self):
        return self.supplier_name



# product model 


class Product(models.Model):
    ProductName = models.CharField(max_length=255)
    Price = models.DecimalField(max_digits=10, decimal_places=2)
    Cost = models.DecimalField(max_digits=10, decimal_places=2)
    Quantity = models.IntegerField()
    Barcode = models.CharField(max_length=255,)  # Blank is True if it is optional
    DateCreated = models.DateTimeField(auto_now_add=True)
    DateUpdated = models.DateTimeField(auto_now=True)
    Supplier = models.ForeignKey('Supplier', on_delete=models.PROTECT)  # Consider using PROTECT or CASCADE
    Category = models.ForeignKey('Category', on_delete=models.PROTECT)  # Consider using PROTECT or CASCADE
    Warehouse = models.ForeignKey('Warehouse', on_delete=models.PROTECT)# Consider using PROTECT or CASCADE
    ExpireDate =  models.DateField(blank=True,null=True)
    Active= models.BooleanField(blank=True),
    Description=models.TextField(blank=True,null=True)
    taxable=models.BooleanField(default=True)
    type = models.CharField(max_length=255, blank=True, null=True)
    discountable= models.BooleanField(default=True)


    def __str__(self):
        return self.ProductName
    
    class Meta:
        ordering = ['-DateUpdated']



# Transcation
class Transaction(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=20)
    transaction_date = models.DateField()
    quantity_change = models.IntegerField()
    transaction_amount = models.DecimalField(max_digits=10, decimal_places=2)







