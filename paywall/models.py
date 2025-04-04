from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

# Create your models here.

class Subscription(models.Model):
    """Track user subscription status"""
    STATUS_CHOICES = (
        ('trial', 'Trial'),
        ('active', 'Active'),
        ('expired', 'Expired'),
    )
    
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='subscription')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='trial')
    trial_start_date = models.DateTimeField(default=timezone.now)
    trial_end_date = models.DateTimeField(null=True, blank=True)
    subscription_end_date = models.DateTimeField(null=True, blank=True)
    payment_id = models.CharField(max_length=100, blank=True, null=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.status}"
    
    def save(self, *args, **kwargs):
        # Set trial end date if not set
        if not self.trial_end_date and self.trial_start_date:
            self.trial_end_date = self.trial_start_date + timedelta(days=30)
        super().save(*args, **kwargs)
    
    @property
    def is_trial_active(self):
        return self.status == 'trial' and timezone.now() <= self.trial_end_date
    
    @property
    def is_paid_active(self):
        return self.status == 'active' and (self.subscription_end_date is None or timezone.now() <= self.subscription_end_date)
    
    @property
    def is_active(self):
        return self.is_trial_active or self.is_paid_active
    
    @property
    def days_left_in_trial(self):
        if not self.is_trial_active:
            return 0
        delta = self.trial_end_date - timezone.now()
        return max(0, delta.days)

class PaymentPlan(models.Model):
    """Available payment plans"""
    PLAN_TYPE_CHOICES = (
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
        ('one_time', 'One-Time'),
    )
    
    PLAN_TIER_CHOICES = (
        ('anza', 'Anza (Starter)'),
        ('endeleza', 'Endeleza (Grow)'),
        ('dumu', 'Dumu (Enterprise)'),
        ('custom', 'Custom One-Time'),
    )
    
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration_days = models.PositiveIntegerField(default=30)
    is_active = models.BooleanField(default=True)
    
    # New fields for enhanced plan features
    plan_type = models.CharField(max_length=20, choices=PLAN_TYPE_CHOICES, default='monthly')
    plan_tier = models.CharField(max_length=20, choices=PLAN_TIER_CHOICES, default='anza')
    business_count = models.PositiveIntegerField(default=1, help_text="Number of businesses allowed")
    has_offline_mode = models.BooleanField(default=False)
    has_multi_device = models.BooleanField(default=False)
    device_access = models.CharField(max_length=100, default="Mobile (Android & iOS Only)")
    has_advanced_inventory = models.BooleanField(default=False)
    has_supplier_integration = models.BooleanField(default=False)
    has_full_financial = models.BooleanField(default=False)
    has_advanced_analytics = models.BooleanField(default=False)
    has_multi_store = models.BooleanField(default=False)
    sms_tier = models.CharField(max_length=20, default="Limited", help_text="SMS tier: Limited, Standard, or Advanced")
    support_tier = models.CharField(max_length=50, default="Email Support")
    featured = models.BooleanField(default=False, help_text="Whether to highlight this plan")
    
    def __str__(self):
        if self.plan_type == 'one_time':
            return f"{self.name} (One-Time)"
        return f"{self.name} ({self.get_plan_type_display()})"
    
    def get_monthly_price(self):
        """Returns the monthly equivalent price for display purposes"""
        if self.plan_type == 'yearly':
            return self.price / 12
        return self.price
    
    def get_savings_percentage(self):
        """Calculate savings percentage for yearly plans compared to monthly"""
        if self.plan_type == 'yearly' and self.plan_tier != 'custom':
            if self.plan_tier == 'anza':
                return 10
            elif self.plan_tier == 'endeleza':
                return 16
            elif self.plan_tier == 'dumu':
                return 17
        return 0

class PaymentHistory(models.Model):
    """Track payment history"""
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE, related_name='payments')
    payment_date = models.DateTimeField(default=timezone.now)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=100)
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    plan = models.ForeignKey(PaymentPlan, on_delete=models.SET_NULL, null=True)
    
    def __str__(self):
        return f"{self.subscription.user.username} - {self.amount} - {self.payment_date}"
