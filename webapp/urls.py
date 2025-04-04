from django.urls import path
from . import views

app_name = 'webapp'  # Add the app_name to set the namespace

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('sales/', views.sales, name='sales'),
    path('stocks/', views.stocks, name='stocks'),
    path('expenses/', views.expenses, name='expenses'),
    path('loans/', views.loans, name='loans'),
    path('suppliers/', views.suppliers, name='suppliers'),
    path('customers/', views.customers, name='customers'),
    path('orders/', views.orders, name='orders'),
    path('reports/', views.reports, name='reports'),
    path('login/', views.login, name='login'),
    path('signup/', views.signup, name='signup'),
    
    # Password reset - direct to templates but use SMS app's API endpoints for processing
    path('forgot-password/', views.forgot_password_page, name='forgot_password'),
    path('reset-password/', views.reset_password_page, name='reset_password'),
    
    # Helper view for developers (DEBUG mode only)
    path('phone-format-help/', views.phone_format_help, name='phone_format_help'),
    path('test-reset/', views.test_reset_page, name='test_reset'),
]