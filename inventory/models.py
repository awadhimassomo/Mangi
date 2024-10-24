import uuid
from django.conf import settings
from django.db import models
from django.apps import apps
from django.forms import ValidationError
from django.utils import timezone
from datetime import timedelta
from django.utils.crypto import get_random_string

import requests


# Category model
class Category(models.Model):
    categoryName = models.CharField(max_length=255)
    unit_choices = [
        ('mls', 'Milliliters'),
        ('l', 'Liters'),
        ('g', 'Grams'),
        ('kg', 'Kilograms'),
        ('doz', 'Dozens'),
        ('pcs', 'Pieces'),
        ('box', 'Boxes'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=True)
    unit = models.CharField(max_length=3, choices=unit_choices, blank=True, null=True)
    unit_quantity = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    business = models.ForeignKey('registration.Business', on_delete=models.CASCADE, default=1)
    type = models.CharField(max_length=255, blank=True, null=True)
    subtype = models.CharField(max_length=255, blank=True, null=True)

    # New fields
    isSynced = models.BooleanField(default=False)
    lastSyncTime = models.DateTimeField(blank=True, null=True)
    isDeleted = models.BooleanField(default=False)

    def __str__(self):
        details = [self.categoryName]
        if self.unit and self.unit_quantity:
            details.append(f'{self.unit_quantity} {self.unit}')
        if self.type:
            details.append(f'Type: {self.type}')
        if self.subtype:
            details.append(f'SubType: {self.subtype}')
        return ' - '.join(details)
    

# Supplier model
class Supplier(models.Model):
    MANUFACTURER = 'Manufacturer'
    DISTRIBUTOR = 'Distributor'
    WHOLESALER = 'Wholesaler'
    RETAILER = 'Retailer'
    OTHER = 'Other'

    supplierType_CHOICES = [
        (MANUFACTURER, 'Manufacturer'),
        (DISTRIBUTOR, 'Distributor'),
        (WHOLESALER, 'Wholesaler'),
        (RETAILER, 'Retailer'),
        (OTHER, 'Other'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=True)
    supplierName  = models.CharField(max_length=255)
    contactPerson = models.CharField(max_length=255)
    contactEmail  = models.EmailField(null=True, blank=True)
    contactPhone  = models.CharField(max_length=15)
    address = models.CharField(max_length=255, null=True, blank=True)
    supplierType = models.CharField(max_length=50, choices=supplierType_CHOICES, default=OTHER)
    business = models.ForeignKey('registration.Business', on_delete=models.CASCADE)
    isSynced = models.BooleanField(default=False)  # Field to track if the record is synced with the server
    isDeleted = models.BooleanField(default=False) 

    def __str__(self):
        return self.supplierName 

class BusinessType(models.Model):
    id = models.AutoField(primary_key=True)  # Explicitly add the ID field
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name
    
class PublicProduct(models.Model):
    product_name = models.CharField(max_length=255)
    barcode = models.CharField(max_length=255, unique=True, default="default_barcode_value")
    businessType = models.ForeignKey(BusinessType, on_delete=models.CASCADE, related_name="public_products")
    description = models.TextField(null=True, blank=True)
    date_added = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.product_name} ({self.barcode})"

    
class ProductBusinessTypeAssociation(models.Model):
    public_product = models.ForeignKey(PublicProduct, on_delete=models.CASCADE, related_name="associations")
    business_type = models.ForeignKey(BusinessType, on_delete=models.CASCADE)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.public_product.product_name} - {self.business_type.name}"

    


# Warehouse model
class Warehouse(models.Model):
    warehouseName = models.CharField(max_length=255)
    warehouseLocation = models.CharField(max_length=255)
    address = models.ForeignKey('registration.Address', on_delete=models.PROTECT, null=True, blank=True)
    business = models.ForeignKey('registration.Business', on_delete=models.CASCADE, null=False)

    def __str__(self):
        return self.warehouseName



class Product(models.Model):
    LOCATION_CHOICES = [
        ('warehouse', 'Warehouse'),
        ('Shop', 'Shop'),
        ('online', 'online'),
    ]

    product_name = models.CharField(max_length=255, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    quantity = models.IntegerField(null=True, blank=True)
    barcode = models.CharField(max_length=255, null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    supplier = models.ForeignKey('Supplier', on_delete=models.PROTECT, null=True, blank=True)
    category = models.ForeignKey('Category', on_delete=models.PROTECT, null=True, blank=True)
    warehouse = models.ForeignKey('Warehouse', on_delete=models.PROTECT, null=True, blank=True)
    expire_date = models.DateField(null=True, blank=True)
    active = models.BooleanField(default=True)
    description = models.TextField(null=True, blank=True)
    taxable = models.BooleanField(default=True)
    product_type = models.CharField(max_length=255, null=True, blank=True)
    discountable = models.BooleanField(default=True)
    business = models.ForeignKey('registration.Business', on_delete=models.CASCADE, null=False)
    isDeleted = models.BooleanField(default=False)
    isSynced = models.BooleanField(default=False)
    lastSyncTime = models.DateTimeField(null=True, blank=True)

    image = models.ImageField(upload_to='product_images/', null=True, blank=True)
    min_stock = models.IntegerField(default=20, null=True, blank=True, help_text="Minimum stock level to trigger restock warning")
    max_stock = models.IntegerField(null=True, blank=True, help_text="Maximum stock level to prevent overstocking")
    location_type = models.CharField(max_length=50, choices=LOCATION_CHOICES, default='store', null=True, blank=True)
    location_identifier = models.CharField(max_length=255, null=True, blank=True, help_text="Specific shelf or aisle in the store")

    class Meta:
        ordering = ['-date_updated']
        unique_together = ('product_name', 'category')  # Ensure unique name-category pairs
        constraints = [
            models.UniqueConstraint(fields=['barcode'], name='unique_barcode')  # Ensure unique barcode
        ]

    def sync_with_public_model(self):
        if not self.barcode:
            return  # Skip if there's no barcode

        PublicProduct = apps.get_model('inventory', 'PublicProduct')
        public_product, created = PublicProduct.objects.get_or_create(
            barcode=self.barcode,
            defaults={
                'product_name': self.product_name,
                'description': self.description,
                'businessType': self.business.businessType,
            }
        )

        if not created:
            pass  # Handle updates to public product here if needed

    def save(self, *args, **kwargs):
        """
        Override the save method to prevent creating duplicates.
        If a product with the same barcode or name-category pair is found, update it instead.
        """
        # Check if a product with the same barcode exists
        if self.barcode:
            existing_product_by_barcode = Product.objects.filter(barcode=self.barcode).exclude(id=self.id).first()
            if existing_product_by_barcode:
                # Update the existing product instead of creating a new one
                existing_product_by_barcode.product_name = self.product_name
                existing_product_by_barcode.price = self.price
                existing_product_by_barcode.quantity += self.quantity
                existing_product_by_barcode.save()
                return

        # Check if a product with the same name and category exists
        if self.product_name and self.category:
            existing_product_by_name_and_category = Product.objects.filter(
                product_name=self.product_name,
                category=self.category
            ).exclude(id=self.id).first()

            if existing_product_by_name_and_category:
                # Update the existing product instead of creating a new one
                existing_product_by_name_and_category.price = self.price
                existing_product_by_name_and_category.quantity += self.quantity
                existing_product_by_name_and_category.save()
                return

        # If no matching product is found, proceed with the standard save
        super().save(*args, **kwargs)
        self.sync_with_public_model()

    def reduce_quantity(self, amount):
        if amount > self.quantity:
            raise ValueError("Cannot reduce quantity below zero")
        self.quantity -= amount
        self.save()
        self.check_and_handle_stock()

    def increase_quantity(self, amount):
        if self.max_stock and (self.quantity + amount) > self.max_stock:
            raise ValueError("Cannot increase quantity beyond max stock level")
        self.quantity += amount
        self.save()

    def check_stock_status(self):
        if self.quantity < self.min_stock:
            return 'Low'
        elif self.max_stock and self.quantity > self.max_stock:
            return 'Overstock'
        else:
            return 'Good'

    def check_and_handle_stock(self):
        stock_status = self.check_stock_status()
        if stock_status == 'Low':
            self.create_preorder()

    def create_preorder(self):
        preorder = Preorder.objects.create(
            product=self,
            supplier=self.supplier,
            quantity_needed=self.min_stock - self.quantity,
            status='Pending',
        )
        response_status = self.trigger_preorder_api(preorder)
        if response_status == 200:
            print("Pre-order notification successfully sent to the frontend.")
        else:
            print("Failed to send pre-order notification to the frontend.")
        supplier_notify_status = self.notify_supplier_about_low_stock(preorder)
        if supplier_notify_status == 200:
            print("Supplier notification successfully sent.")
        else:
            print("Failed to send supplier notification.")

    def trigger_preorder_api(self, preorder):
        api_url = 'http://192.168.1.197:8000/inventory/preorder-notification/'
        payload = {
            'preorder_id': preorder.id,
            'product_name': self.product_name,
            'quantity_needed': preorder.quantity_needed,
        }
        response = requests.post(api_url, json=payload)
        return response.status_code

    def notify_supplier_about_low_stock(self, preorder):
        api_url = 'http://192.168.1.197:8000/inventory/notify-supplier/'
        payload = {
            'supplier_id': preorder.supplier.id,
            'product_name': self.product_name,
            'quantity_needed': preorder.quantity_needed,
            'user': self.business.name,
        }
        response = requests.post(api_url, json=payload)
        return response.status_code

    def __str__(self):
        return self.product_name




class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('cash', 'Cash'),
        ('lipa_namba', 'Lipa Kwa Simu'),
        ('bank_transfer', 'Bank Transfer'),
        ('credit_card', 'Credit Card'),
        ('loan', 'Loan'),
        ('other', 'Other'),
    ]
  
  
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=True  # Allow editing
    )  
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    transaction_date = models.DateField(default=timezone.now)
    business= models.ForeignKey('registration.Business', on_delete=models.CASCADE, null=False)
    customer = models.ForeignKey('registration.Customer', on_delete=models.SET_NULL, null=True, blank=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    outstanding_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_synced = models.BooleanField(default=False)  # Tracks whether the transaction has been synced with the server
    is_deleted = models.BooleanField(default=False)  # Tracks whether the transaction has been marked as deleted


#This method will create a preorder then send a notification to the frontend then when confirm it will delete it and create an actually order

class DraftOrder(models.Model):
    STATUS_CHOICES = [
        ('Draft', 'Draft'),
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]

    draft_number = models.CharField(max_length=50, unique=True, default=get_random_string)
    supplier = models.ForeignKey('Supplier', on_delete=models.CASCADE)
    business = models.ForeignKey('registration.Business', on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Draft')
    notes = models.TextField(null=True, blank=True)

    def convert_to_order(self):
        # Create the actual order
        order = Order.objects.create(
            order_number=self.draft_number,
            supplier=self.supplier,
            business=self.business,
            order_date=self.created_date,
            status=self.status,
            notes=self.notes,
        )
        
        # Delete the draft order after successfully creating the actual order
        self.delete()
        
        return order

    def __str__(self):
        return f"Draft Order {self.draft_number} - {self.supplier.name}"


    
class Order(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order_number = models.CharField(max_length=50, unique=True)
    supplier = models.ForeignKey('Supplier', on_delete=models.CASCADE)
    business = models.ForeignKey('registration.Business', on_delete=models.CASCADE)
    order_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    delivery_date = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    token = models.CharField(max_length=32, unique=True, blank=True, null=True)  # Token field

    def __str__(self):
        return f"Order {self.order_number} - {self.supplier.supplierName}"

    def save(self, *args, **kwargs):
        # Generate a unique token if it doesn't already exist
        if not self.token:
            self.token = get_random_string(length=32)
        super().save(*args, **kwargs)

class OrderItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product_id = models.ForeignKey('Product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    
    def __str__(self):
        product = Product.objects.get(id=self.product_id)
        return f"{self.quantity} x {product.product_name} in Order {self.order.order_number}"


# Purchase model
class Purchase(models.Model):
   
    business = models.ForeignKey('registration.Business', on_delete=models.CASCADE)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, related_name='purchases', on_delete=models.CASCADE,default=1)  # Link to Order model
    transaction = models.OneToOneField(Transaction, on_delete=models.CASCADE, primary_key=True)
    quantity = models.IntegerField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    outstanding_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, blank=True, null=True)
    is_paid = models.BooleanField(default=False)
    
    # Additional fields for LPO and Invoice
    purchase_order_number = models.CharField(max_length=20, unique=True, default=1)
    lpo_date = models.DateField(default=timezone.now) 
    invoice_number = models.CharField(max_length=20, blank=True, null=True)
    payment_terms = models.CharField(max_length=100, blank=True, null=True)
    
    def __str__(self):
        return f'Purchase: {self.supplier.name} - {self.product.product_name} - {self.quantity}'

    def save(self, *args, **kwargs):
        # Calculate the total amount based on product cost and quantity
        self.total_amount = self.product.cost * self.quantity
        super().save(*args, **kwargs)
        
class Sales(models.Model):
     
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=True  # Allow editing
    )
    transaction_id  = models.ForeignKey(Transaction, on_delete=models.CASCADE)
    business = models.ForeignKey('registration.Business', on_delete=models.CASCADE)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    isSynced = models.BooleanField(default=False)  # Tracks if the sale is synced with the remote system
    isDeleted = models.BooleanField(default=False)  # Marks if the sale is deleted (soft delete)
    
    def __str__(self):
        return f"Sale {self.id} for transaction {self.transaction_id}"

    def soft_delete(self):
        """ Soft delete the sale by setting isDeleted to True """
        self.isDeleted = True
        self.save()

    def mark_synced(self):
        """ Mark the sale as synced """
        self.isSynced = True
        self.save()


class SalesItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sale = models.ForeignKey(Sales, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.IntegerField()
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product.product_name} (Sale ID: {self.sale.id})"




class Installment(models.Model):
    REMINDER_CHOICES = [
        ('3_days', '3 Days'),
        ('1_week', '1 Week'),
        ('2_weeks', '2 Weeks'),
        ('1_month', '1 Month'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    transaction_id = models.ForeignKey('Transaction', on_delete=models.CASCADE)
    customer = models.ForeignKey('registration.Customer', on_delete=models.CASCADE, null=True, blank=True, related_name='installments')
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, null=True, blank=True, related_name='installments')
    due_date = models.DateField(blank=True, null=True)
    amount_due = models.DecimalField(max_digits=15, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    reminder_sent = models.BooleanField(default=False)
    business = models.ForeignKey('registration.Business', on_delete=models.CASCADE, default=1)
    
    reminder_interval = models.CharField(max_length=10, choices=REMINDER_CHOICES, default='3_days')
    last_reminder_sent = models.DateField(blank=True, null=True)
    last_payment_date = models.DateField(blank=True, null=True)

    def __str__(self):
        entity = self.customer or self.supplier
        entity_type = "Customer" if self.customer else "Supplier"
        return f'Installment: {self.transaction_id} - Due: {self.due_date or "No due date set"} - {entity_type}: {entity}'

    def should_send_reminder(self):
        if not self.due_date:
            return False
        
        if not self.last_reminder_sent:
            return True
        
        next_reminder_date = None
        if self.reminder_interval == '3_days':
            next_reminder_date = self.last_reminder_sent + timedelta(days=3)
        elif self.reminder_interval == '1_week':
            next_reminder_date = self.last_reminder_sent + timedelta(weeks=1)
        elif self.reminder_interval == '2_weeks':
            next_reminder_date = self.last_reminder_sent + timedelta(weeks=2)
        elif self.reminder_interval == '1_month':
            next_reminder_date = self.last_reminder_sent + timedelta(days=30)
        
        return timezone.now().date() >= next_reminder_date

    def record_payment(self, payment_amount):
        self.amount_paid += payment_amount
        self.last_payment_date = timezone.now().date()
        self.save()

    def is_fully_paid(self):
        return self.amount_paid >= self.amount_due

    def clean(self):
        if not (self.customer or self.supplier):
            raise ValidationError('Either a customer or supplier must be set.')
        if self.customer and self.supplier:
            raise ValidationError('Only one of customer or supplier can be set.')



class Expense(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('Cash', 'Cash'),
        ('Loan', 'Loan'),
    ]

    CATEGORY_CHOICES = [
        ('Travel', 'Travel'),
        ('Supplies', 'Supplies'),
        ('Meals', 'Meals'),
        ('Other', 'Other'),  # Add other categories as needed
    ]

    date = models.DateField(default=timezone.now)
    without_tax_cost = models.DecimalField(max_digits=10, decimal_places=2)
    with_tax_cost = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    approval_status = models.BooleanField(default=False)
    receipt = models.FileField(upload_to='receipts/', null=True, blank=True)
    vendor = models.CharField(max_length=255, null=True, blank=True)
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHOD_CHOICES, default='Cash')
    notes = models.TextField(null=True, blank=True)
    business = models.ForeignKey('registration.Business', on_delete=models.CASCADE)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, null=True)  

    def __str__(self):
        return f"{self.vendor} - Total: {self.total}"

    def clean(self):
        # Validate expense against ExpenseTerms
        self.validate_expense_terms()

    def validate_expense_terms(self):
        # Get the user's role
        user_role = self.business.owner.role  # Assuming the Business model has an owner field
        
        # Fetch relevant policies based on the user's role and category
        policies = ExpenseTerms.objects.filter(
            impacted_roles=user_role,
            category=self.category  # Filter by category
        )

        if not policies.exists():
            raise ValidationError("No applicable expense policy for the selected category.")

        for policy in policies:
            if self.total > policy.max_amount:
                raise ValidationError(
                    f"Total amount exceeds the maximum allowed for this policy: {policy.policy_description}"
                )
            if self.date.day != policy.enforcement_day:
                raise ValidationError(
                    f"Expense date must be on the enforcement day of this policy: {policy.policy_description}"
                )

    def save(self, *args, **kwargs):
        self.clean()  # Call the clean method to enforce validation
        super().save(*args, **kwargs)


class ExpenseTerms(models.Model):

    CATEGORY_CHOICES = [
    ('Travel', 'Travel'),
    ('Supplies', 'Supplies'),
    ('Meals', 'Meals'),
    ('Other', 'Other'),  # Add more categories as necessary
]
    # Define roles as choices
    ROLE_CHOICES = [
        ('management', 'Management'),
        ('sales', 'Sales'),
        ('general', 'General Team'),
    ]

    # Policy details
    policy_description = models.TextField()  # Detailed description of the policy
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, null=True,default=0)  # Make it nullable temporarily
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    max_amount = models.DecimalField(max_digits=10, decimal_places=2)  # Maximum allowed amount
    enforcement_day = models.IntegerField()  # Day for enforcement (1-31)
    impacted_roles = models.CharField(max_length=20, choices=ROLE_CHOICES)  # Roles impacted by this policy
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # User who created the policy
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp when the policy was created

    def __str__(self):
        return f"{self.policy_description} - Max: {self.max_amount} - Role: {self.impacted_roles}"
