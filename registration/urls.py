# urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RegisterUserView, RegisterBusinessView

router = DefaultRouter()
router.register(r'users', RegisterUserView, basename='users')  # Specify basename 'users'
router.register(r'businesses', RegisterBusinessView, basename='businesses')  # Specify basename 'businesses'

urlpatterns = [
    path('', include(router.urls)),
]
