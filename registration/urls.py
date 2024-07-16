# urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RegisterUserView, RegisterBusinessView,login_view,switch_business
from .views import delete_user, update_user
from .views import delete_business, update_business, list_users, get_routes, logout_view
from .views import get_business_type

router = DefaultRouter()
router.register(r'users', RegisterUserView, basename='users')  # Specify basename 'users'
router.register(r'businesses', RegisterBusinessView, basename='businesses')  # Specify basename 'businesses'
 # Specify basename 'get_routes'


urlpatterns = [
    path('', include(router.urls)),
    path('login/', login_view, name='login'),
    path('switch_business/', switch_business, name='switch_business'),
    path('delete_user/<int:pk>/', delete_user, name='delete_user'),
    path('update_user/<int:pk>/', update_user, name='update_user'),
    path('delete_business/<int:pk>/', delete_business, name='delete_business'),
    path('update_business/<int:pk>/', update_business, name='update_business'),
    path('list_users/', list_users, name='list_users'),
    path('routes/', get_routes, name='get_routes'),
    path('get-business-type/', get_business_type, name='get-business-type'),
    path('logout/', logout_view, name='logout'),
      
]
    

