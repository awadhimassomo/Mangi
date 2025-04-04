from django.contrib import admin
from .models import Subscription, PaymentPlan, PaymentHistory

# Register your models here.

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'status', 'trial_start_date', 'trial_end_date', 'subscription_end_date', 'is_active')
    list_filter = ('status',)
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('is_trial_active', 'is_paid_active', 'is_active', 'days_left_in_trial')

@admin.register(PaymentPlan)
class PaymentPlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'duration_days', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')

@admin.register(PaymentHistory)
class PaymentHistoryAdmin(admin.ModelAdmin):
    list_display = ('subscription', 'payment_date', 'amount', 'payment_method', 'transaction_id')
    list_filter = ('payment_date', 'payment_method')
    search_fields = ('subscription__user__username', 'transaction_id')
