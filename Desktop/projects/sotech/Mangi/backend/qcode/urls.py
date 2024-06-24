from django.urls import path
from .views import getRoutes, getQCodes, QRCodeAPIView

app_name = 'qcode'

urlpatterns = [
    path('create/', QRCodeAPIView.as_view(), name='create_qrcode'),
    path('code/', getQCodes, name='get_qrcodes'),
    path('', getRoutes, name='api_routes'),
]