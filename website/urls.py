from django.urls import path
from django.views.generic import TemplateView
from . import views

urlpatterns = [
    path('', views.index, name='index'),  # Example URL pattern
    path('developer/', TemplateView.as_view(template_name='developer.html'), name='developer'),
    path('order/<str:token>/', views.order_detail, name='order_detail'),
    path('order_pdf/<str:token>/', views.generate_order_pdf, name='generate_order_pdf'),
      path('privacy-policy/', views.PrivacyPolicyView.as_view(), name='privacy_policy'),
]
