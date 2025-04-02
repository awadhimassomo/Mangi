# sms/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import NetworkCreditViewSet, OTPVerificationView,ResendOTPView, OTPCreditViewSet, SendOTPView, VerifyOTPView, daily_report_view
from .views import SendCreditView, add_credit_view, credit_success_view,PasswordResetRequestView,PasswordResetConfirmView

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'network-credits', NetworkCreditViewSet)
router.register(r'otp-credits', OTPCreditViewSet)

# Define the URL patterns.
urlpatterns = [
    path('', include(router.urls)),  # Include the router URLs
    path('send-otp/', SendOTPView.as_view(), name='send_otp'),  # Add the send-otp view
    path('send-credits/', SendCreditView.as_view(), name='send_credit'),  # Add the send-credit view
    path('add-credit/', add_credit_view, name='add_credit'), 
    path('resend-otp/', ResendOTPView.as_view(), name='resend-otp'), # Add the add-credit view
    path('credit-success/', credit_success_view, name='credit_success'),
    path('verify-otp/',VerifyOTPView.as_view(), name='verify-otp'),  # Add the credit-success view
    path('passwordrest/',PasswordResetRequestView.as_view(), name='passwordrest'),
    path('daily-report/', daily_report_view, name='daily_report'),
    path('reset-otp/',OTPVerificationView.as_view(), name='verify-otp'), 
    path('password-reset/', PasswordResetConfirmView.as_view(), name='password-reset'),
    
]

