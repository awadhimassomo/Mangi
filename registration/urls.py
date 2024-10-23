# urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from inventory import views
from .views import BusinessDetailView, BusinessListView, RegisterUserView, RegisterBusinessView, create_partner, delete_partner, list_partners,login_view, register_customer, retrieve_partner,switch_business, sync_customers, update_partner
from .views import delete_user, update_user
from .views import delete_business, update_business, list_users, get_routes, logout_view
from .views import get_businessType


router = DefaultRouter()
router.register(r'users', RegisterUserView, basename='users')  # Specify basename 'users'

# Specify basename 'businesses'
 # Specify basename 'get_routes'


urlpatterns = [
    path('', include(router.urls)),
    path('login/', login_view, name='login'),
    # path('user_exists/', user_exists, name='user_exists'), # to be implemented
    path('switch_business/', switch_business, name='switch_business'),
    path('delete_user/<int:pk>/', delete_user, name='delete_user'),
    path('update_user/<int:pk>/', update_user, name='update_user'),
    path('delete_business/<int:pk>/', delete_business, name='delete_business'),
    path('update_business/<int:pk>/', update_business, name='update_business'),
    path('list_users/', list_users, name='list_users'),
    path('routes/', get_routes, name='get_routes'),
    path('get-business-type/', get_businessType, name='get-business-type'),
    path('logout/', logout_view, name='logout'),
    path('register_customer/', register_customer, name='register_customer'),
    path('businesse/', RegisterBusinessView.as_view({'post': 'register'}), name='register-business'),
    path('businesses/', BusinessListView.as_view(), name='business-list'),
    path('businesses/<int:id>/', BusinessDetailView.as_view(), name='business-detail'),
    path('partners/', list_partners, name='list_partners'),
    path('partners/create/', create_partner, name='create_partner'),
    path('partners/<int:pk>/', retrieve_partner, name='retrieve_partner'),
    path('partners/update/<int:pk>/', update_partner, name='update_partner'),
    path('partners/delete/<int:pk>/', delete_partner, name='delete_partner'),
    path('businesses/', BusinessListView.as_view(), name='business_list'),
    path('customers/sync-customers/', sync_customers, name='sync_customers'),
      
]
    

