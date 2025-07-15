from django.db import models
from django.utils import timezone
import uuid
from registration.models import Business, Customer
from inventory.models import Product, Supplier

# Core Accounting Models

class Account(models.Model):
    """Chart of Accounts model"""
    ACCOUNT_TYPES = [
        ('ASSET', 'Asset'),
        ('LIABILITY', 'Liability'),
        ('EQUITY', 'Equity'),
        ('INCOME', 'Income'),
        ('EXPENSE', 'Expense'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=10)
    name = models.CharField(max_length=100)
    account_type = models.CharField(max_length=10, choices=ACCOUNT_TYPES)
    parent_code = models.CharField(max_length=10, null=True, blank=True)
    business = models.ForeignKey('registration.Business', on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = [['code', 'business']]
    
    def __str__(self):
        return f"{self.code} - {self.name}"

class JournalEntry(models.Model):
    """Header for accounting journal entries"""
    SOURCE_TYPES = [
        ('SALE', 'Sales Transaction'),
        ('PURCHASE', 'Purchase Transaction'),
        ('INVENTORY', 'Inventory Adjustment'),
        ('JOURNAL', 'Journal Entry'),
        ('PAYMENT', 'Payment'),
        ('RECEIPT', 'Receipt'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    date = models.DateTimeField(default=timezone.now)
    entry_type = models.CharField(max_length=10, choices=SOURCE_TYPES)
    reference = models.CharField(max_length=50)
    business = models.ForeignKey('registration.Business', on_delete=models.CASCADE)
    customer = models.ForeignKey('registration.Customer', on_delete=models.SET_NULL, null=True, blank=True)
    supplier = models.ForeignKey('inventory.Supplier', on_delete=models.SET_NULL, null=True, blank=True, related_name='journal_entries')
    memo = models.TextField(blank=True, null=True)
    created_by = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_posted = models.BooleanField(default=False)
    posting_date = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.entry_type} #{self.reference}"
    
    def post(self):
        """Post the journal entry to the ledger"""
        if not self.is_posted:
            self.is_posted = True
            self.posting_date = timezone.now()
            self.save()
    
    @property
    def is_balanced(self):
        """Check if debits equal credits"""
        debits_sum = sum(line.debit_amount for line in self.lines.all())
        credits_sum = sum(line.credit_amount for line in self.lines.all())
        return debits_sum == credits_sum

class JournalLine(models.Model):
    """Line items for journal entries"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    journal = models.ForeignKey(JournalEntry, on_delete=models.CASCADE, related_name='lines')
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    description = models.CharField(max_length=255, blank=True, null=True)
    debit_amount = models.PositiveIntegerField(default=0)  # Stored in minor units (cents)
    credit_amount = models.PositiveIntegerField(default=0)  # Stored in minor units (cents)
    tax_code = models.CharField(max_length=10, blank=True, null=True)
    tax_amount = models.PositiveIntegerField(default=0)  # Stored in minor units (cents)
    product = models.ForeignKey('inventory.Product', on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.journal.reference} - {self.account.name}"

# Reporting Support Models

class ReportConfiguration(models.Model):
    """Configuration for report layout and preferences"""
    REPORT_TYPES = [
        ('B1', 'Cashbook'),
        ('B2', 'Sales Day Book'),
        ('B3', 'Purchases Day Book'),
        ('B4', 'General Journal'),
        ('B5', 'General Ledger'),
        ('B6', 'Inventory Ledger'),
        ('R1', 'Trial Balance'),
        ('R2', 'Income Statement'),
        ('R3', 'Balance Sheet'),
        ('R4', 'Cash-Flow Statement'),
        ('R5', 'Accounts Receivable Aging'),
        ('R6', 'Accounts Payable Aging'),
        ('R7', 'VAT / GST Summary'),
        ('R8', 'Expense Register'),
        ('R9', 'Bank Reconciliation'),
        ('R10', 'Inventory Valuation'),
        ('R11', 'Stock Movement'),
        ('R12', 'Gross-Profit by Item/Category'),
        ('R13', 'Daily Z-Report'),
        ('R14', 'KPI Dashboard'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    business = models.ForeignKey('registration.Business', on_delete=models.CASCADE)
    report_type = models.CharField(max_length=10, choices=REPORT_TYPES)
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    default_date_range = models.IntegerField(default=30)  # Default days to look back
    include_zero_balances = models.BooleanField(default=False)
    custom_config = models.JSONField(blank=True, null=True)  # For report-specific settings
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('business', 'report_type')
    
    def __str__(self):
        return f"{self.business.businessName} - {self.get_report_type_display()}"

class SavedReport(models.Model):
    """For storing generated reports"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    business = models.ForeignKey('registration.Business', on_delete=models.CASCADE)
    report_type = models.CharField(max_length=10, choices=ReportConfiguration.REPORT_TYPES)
    name = models.CharField(max_length=100)
    date_generated = models.DateTimeField(default=timezone.now)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    report_data = models.JSONField()
    parameters = models.JSONField(blank=True, null=True)  # Stores the parameters used to generate the report
    created_by = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} ({self.date_generated.strftime('%Y-%m-%d')})"

class FiscalYear(models.Model):
    """Fiscal year configuration for accounting periods"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    business = models.ForeignKey('registration.Business', on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('business', 'name')
    
    def __str__(self):
        return f"{self.name} ({self.start_date.strftime('%Y-%m-%d')} to {self.end_date.strftime('%Y-%m-%d')})"

class FiscalPeriod(models.Model):
    """Fiscal periods (e.g., months) within a fiscal year"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    fiscal_year = models.ForeignKey(FiscalYear, on_delete=models.CASCADE, related_name='periods')
    name = models.CharField(max_length=50)
    start_date = models.DateField()
    end_date = models.DateField()
    is_closed = models.BooleanField(default=False)
    closing_date = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.name} ({self.fiscal_year.name})"

class TaxCode(models.Model):
    """Tax codes for VAT/GST reporting"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    business = models.ForeignKey('registration.Business', on_delete=models.CASCADE)
    code = models.CharField(max_length=10)
    name = models.CharField(max_length=100)
    rate = models.DecimalField(max_digits=5, decimal_places=2)
    is_active = models.BooleanField(default=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('business', 'code')
    
    def __str__(self):
        return f"{self.code} - {self.name} ({self.rate}%)"
