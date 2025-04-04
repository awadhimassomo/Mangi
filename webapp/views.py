from django.shortcuts import render
import os
import json
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie

# Create your views here.
def dashboard(request):
    """
    View function for the dashboard page
    """
    # You can add context data here to pass to the template
    context = {
        'title': 'Business Dashboard',
        # Add more context data as needed
    }
    
    # Use a more specific template path
    template_path = os.path.join('webapp', 'dashboard.html')
    print(f"Looking for template at: {template_path}")
    
    return render(request, template_path, context)

def sales(request):
    """
    View function for the sales page.
    """
    return render(request, 'webapp/sales.html')


def stocks(request):
    """
    View function for the stocks page.
    """
    return render(request, 'webapp/stocks.html')


def expenses(request):
    """
    View function for the expenses page.
    """
    return render(request, 'webapp/Expenses.html')


def loans(request):
    """
    View function for the loans page.
    """
    return render(request, 'webapp/loans.html')


def suppliers(request):
    """
    View function for the suppliers page.
    """
    return render(request, 'webapp/suppliers.html')


def customers(request):
    """
    View function for the customers page.
    """
    return render(request, 'webapp/customers.html')


def orders(request):
    """
    View function for the purchase orders page (orders to suppliers).
    """
    return render(request, 'webapp/orders.html')


def reports(request):
    """
    View function for the reports and analytics page.
    """
    return render(request, 'webapp/reports.html')


@ensure_csrf_cookie
def login(request):
    """
    View function for the login page.
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            phone_number = data.get('phoneNumber')
            password = data.get('password')
            remember_me = data.get('rememberMe', False)
            
            # Here you would typically authenticate the user
            # For now, we'll just return dummy successful response
            # In a real app, you'd verify credentials and generate tokens
            
            # Set session expiration based on remember_me flag
            if remember_me:
                # Set session to expire in 30 days (or your preferred duration)
                request.session.set_expiry(60 * 60 * 24 * 30)  # 30 days in seconds
            else:
                # Use default session expiration (browser close)
                request.session.set_expiry(0)
            
            # Dummy success response for testing
            return JsonResponse({
                'access': 'dummy_access_token',
                'refresh': 'dummy_refresh_token',
                'username': 'Test User',
                'email': 'test@example.com',
                'phoneNumber': phone_number,
                'role': 'owner',
                'is_staff': True,
                'owner_id': 1,
                'businesses': [
                    {
                        'id': 1,
                        'name': 'Test Business',
                        'type': 'retail'
                    }
                ]
            })
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        # For GET requests, render the login template
        return render(request, 'webapp/login.html')


def signup(request):
    """
    View function for the signup page.
    """
    return render(request, 'webapp/Signup.html')


def forgot_password_page(request):
    """
    View function for the forgot password page.
    This only renders the template. The actual API calls are made directly to the SMS app endpoints.
    """
    return render(request, 'webapp/forgot_password.html')


def reset_password_page(request):
    """
    View function for the reset password page.
    This only renders the template. The actual API calls are made directly to the SMS app endpoints.
    """
    return render(request, 'webapp/reset_password.html')


def phone_format_help(request):
    """
    Developer helper view to show valid phone numbers in the database.
    This helps when testing the password reset functionality.
    Only available in DEBUG mode.
    """
    from django.conf import settings
    from django.http import JsonResponse
    from django.contrib.auth import get_user_model
    
    if not settings.DEBUG:
        return JsonResponse({'error': 'This view is only available in DEBUG mode'}, status=403)
    
    User = get_user_model()
    # Get a sample of phone numbers from the database (for testing only)
    sample_users = User.objects.all().values('phoneNumber')[:5]
    
    return JsonResponse({
        'message': 'This is a developer helper to show valid phone formats in the database.',
        'note': 'Use these phone numbers when testing the password reset functionality.',
        'phone_format_tips': [
            'Phone numbers should be entered in the format: 255XXXXXXXXX',
            'Do not use a leading + sign',
            'Do not use a leading 0',
            'Do not include spaces or dashes',
        ],
        'sample_phone_numbers': [user['phoneNumber'] for user in sample_users if user['phoneNumber']]
    })


def test_reset_page(request):
    """
    Developer tool page for testing the SMS app's password reset API with different phone number formats.
    """
    return render(request, 'webapp/test_reset.html')
