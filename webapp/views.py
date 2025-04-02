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
            
            # Here you would typically authenticate the user
            # For now, we'll just return dummy successful response
            # In a real app, you'd verify credentials and generate tokens
            
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
