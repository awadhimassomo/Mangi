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
]