from django.urls import path
from . import views

app_name = 'paywall'

urlpatterns = [
    path('subscription/', views.subscription_page, name='subscription'),
    path('payment/<int:plan_id>/', views.payment_page, name='payment'),
    path('process-payment/', views.process_payment, name='process_payment'),
    path('payment-history/', views.payment_history, name='payment_history'),
    path('manual-update/<int:user_id>/', views.manual_subscription_update, name='manual_update'),
    path('phone-update/', views.update_subscription_by_phone, name='phone_update'),
    path('api/check-status/', views.check_subscription_status, name='check_status'),
]
