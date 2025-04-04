from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.urls import reverse
from django.contrib.auth import get_user_model
from datetime import timedelta

from .models import Subscription, PaymentPlan, PaymentHistory

@login_required
def subscription_page(request):
    """
    Display subscription status and payment options
    """
    # Get user's subscription
    subscription, created = Subscription.objects.get_or_create(
        user=request.user,
        defaults={
            'status': 'trial',
            'trial_start_date': timezone.now(),
        }
    )
    
    # Get available payment plans
    payment_plans = PaymentPlan.objects.filter(is_active=True)
    
    context = {
        'subscription': subscription,
        'payment_plans': payment_plans,
        'days_left': subscription.days_left_in_trial,
    }
    
    return render(request, 'paywall/subscription.html', context)

@login_required
def payment_page(request, plan_id):
    """
    Display payment form for a specific plan
    """
    try:
        plan = PaymentPlan.objects.get(id=plan_id, is_active=True)
    except PaymentPlan.DoesNotExist:
        messages.error(request, "Selected plan is not available.")
        return redirect('paywall:subscription')
    
    context = {
        'plan': plan,
    }
    
    return render(request, 'paywall/payment.html', context)

@login_required
@require_POST
def process_payment(request):
    """
    Process payment and update subscription status
    
    This is a simplified version. In a real-world scenario,
    you would integrate with a payment gateway like Stripe or PayPal.
    """
    plan_id = request.POST.get('plan_id')
    payment_method = request.POST.get('payment_method')
    
    try:
        plan = PaymentPlan.objects.get(id=plan_id, is_active=True)
    except PaymentPlan.DoesNotExist:
        messages.error(request, "Selected plan is not available.")
        return redirect('paywall:subscription')
    
    # Get user subscription
    subscription, created = Subscription.objects.get_or_create(
        user=request.user,
        defaults={
            'status': 'trial',
            'trial_start_date': timezone.now(),
        }
    )
    
    # Update subscription status to active
    subscription.status = 'active'
    
    # Set subscription end date based on plan duration
    if subscription.subscription_end_date and subscription.subscription_end_date > timezone.now():
        # If subscription is still active, extend it
        subscription.subscription_end_date = subscription.subscription_end_date + timezone.timedelta(days=plan.duration_days)
    else:
        # Otherwise, start from today
        subscription.subscription_end_date = timezone.now() + timezone.timedelta(days=plan.duration_days)
    
    # Generate a mock payment ID
    payment_id = f"PAY-{timezone.now().strftime('%Y%m%d%H%M%S')}-{request.user.id}"
    subscription.payment_id = payment_id
    subscription.save()
    
    # Create payment history record
    PaymentHistory.objects.create(
        subscription=subscription,
        amount=plan.price,
        payment_method=payment_method,
        transaction_id=payment_id,
        plan=plan
    )
    
    messages.success(request, f"Payment successful! Your subscription is active until {subscription.subscription_end_date.strftime('%Y-%m-%d')}.")
    return redirect('paywall:subscription')

@login_required
def payment_history(request):
    """
    Display payment history for the user
    """
    try:
        subscription = request.user.subscription
        payments = PaymentHistory.objects.filter(subscription=subscription).order_by('-payment_date')
    except:
        payments = []
    
    context = {
        'payments': payments
    }
    
    return render(request, 'paywall/payment_history.html', context)

@login_required
def manual_subscription_update(request, user_id):
    """
    Manually update a user's subscription status (admin only)
    """
    # Check if user is staff or admin
    if not request.user.is_staff and not request.user.is_superuser:
        return redirect('subscription_page')
    
    try:
        # Get the target user
        User = get_user_model()
        target_user = User.objects.get(id=user_id)
        
        # Get or create their subscription
        subscription, created = Subscription.objects.get_or_create(
            user=target_user,
            defaults={
                'status': 'trial',
                'trial_start_date': timezone.now(),
            }
        )
        
        if request.method == 'POST':
            # Get form data
            status = request.POST.get('status', 'active')
            duration_days = int(request.POST.get('duration_days', 365))
            
            # Update subscription
            subscription.status = status
            subscription.subscription_end_date = timezone.now() + timedelta(days=duration_days)
            subscription.save()
            
            # Create payment history record
            PaymentHistory.objects.create(
                subscription=subscription,
                amount=0,  # Manual update, no payment
                payment_method="Manual Update",
                transaction_id=f"manual-{timezone.now().timestamp()}",
                plan=None
            )
            
            messages.success(request, f"Subscription for {target_user.username} updated successfully")
            return redirect('admin_dashboard')  # Replace with your admin dashboard URL
        
        context = {
            'target_user': target_user,
            'subscription': subscription,
        }
        
        return render(request, 'paywall/manual_subscription_update.html', context)
        
    except User.DoesNotExist:
        messages.error(request, "User not found")
        return redirect('admin_dashboard')  # Replace with your admin dashboard URL

@login_required
def update_subscription_by_phone(request):
    """
    Manually update a user's subscription by phone number (admin only)
    """
    # Check if user is staff or admin
    if not request.user.is_staff and not request.user.is_superuser:
        return redirect('subscription_page')
    
    phone_number = request.POST.get('phone_number', '+255713091865')  # Default to the specified number
    
    try:
        # Get the target user by phone number
        User = get_user_model()
        target_user = User.objects.get(phoneNumber=phone_number)
        
        # Get or create their subscription
        subscription, created = Subscription.objects.get_or_create(
            user=target_user,
            defaults={
                'status': 'trial',
                'trial_start_date': timezone.now(),
            }
        )
        
        if request.method == 'POST' and 'update_subscription' in request.POST:
            # Get form data
            status = request.POST.get('status', 'active')
            duration_days = int(request.POST.get('duration_days', 365))
            
            # Update subscription
            subscription.status = status
            subscription.subscription_end_date = timezone.now() + timedelta(days=duration_days)
            subscription.save()
            
            # Create payment history record
            PaymentHistory.objects.create(
                subscription=subscription,
                amount=0,  # Manual update, no payment
                payment_method="Manual Update by Phone",
                transaction_id=f"manual-phone-{timezone.now().timestamp()}",
                plan=None
            )
            
            messages.success(request, f"Subscription for {target_user.phoneNumber} updated successfully")
            return redirect('admin_dashboard')  # Replace with your admin dashboard URL
        
        context = {
            'target_user': target_user,
            'subscription': subscription,
            'phone_number': phone_number,
        }
        
        return render(request, 'paywall/phone_subscription_update.html', context)
        
    except User.DoesNotExist:
        if request.method == 'GET':
            return render(request, 'paywall/phone_subscription_update.html', {'phone_number': phone_number})
        
        messages.error(request, f"User with phone number {phone_number} not found")
        return redirect('admin_dashboard')  # Replace with your admin dashboard URL

def check_subscription_status(request):
    """
    API endpoint to check subscription status
    Used by frontend to show notifications
    """
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Not authenticated'}, status=401)
    
    try:
        subscription = request.user.subscription
        data = {
            'status': subscription.status,
            'is_active': subscription.is_active,
            'days_left': subscription.days_left_in_trial,
            'subscription_end_date': subscription.subscription_end_date.isoformat() if subscription.subscription_end_date else None,
        }
        return JsonResponse(data)
    except:
        return JsonResponse({
            'status': 'unknown',
            'is_active': False
        })
