from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone
from django.conf import settings
from django.contrib import messages

class PaywallMiddleware:
    """
    Middleware to enforce the 30-day trial paywall
    
    This middleware checks if the user's trial period is active or
    if they have an active paid subscription. If neither is true,
    they are redirected to the subscription page.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        # Always allow access to the admin site and paywall-related URLs
        if (
            request.path.startswith('/admin') or 
            request.path.startswith('/static') or
            request.path.startswith('/subscription') or
            request.path.startswith('/payment') or
            request.path.startswith('/accounts') or
            request.path.startswith('/sms/') or  # Exempt SMS related pages
            request.path == '/'
        ):
            return self.get_response(request)
            
        # Check if user is authenticated
        if request.user.is_authenticated:
            # Allow staff and superusers to bypass subscription check
            if request.user.is_staff or request.user.is_superuser:
                return self.get_response(request)
                
            # Try to get the user's subscription
            try:
                subscription = request.user.subscription
                
                # Allow access if subscription is active
                if subscription.is_active:
                    # Show notification if trial is nearing expiration (less than 5 days left)
                    if subscription.status == 'trial' and subscription.days_left_in_trial <= 5:
                        messages.warning(
                            request, 
                            f"Your trial expires in {subscription.days_left_in_trial} days. "
                            f"<a href='{reverse('paywall:subscription')}'>Upgrade now</a> to continue using all features."
                        )
                    return self.get_response(request)
                    
                # Redirect to subscription page if not active
                return redirect('paywall:subscription')
                
            except (AttributeError, Exception):
                # If no subscription exists, redirect to subscription page
                return redirect('paywall:subscription')
                
        # For non-authenticated users, continue normal flow
        return self.get_response(request)
