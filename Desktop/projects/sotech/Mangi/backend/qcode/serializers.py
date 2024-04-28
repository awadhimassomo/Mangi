from rest_framework import serializers
from inventory.serializers import ProductSerializer
from .models import QRCode
from inventory.models import Product

#qrcode
class QRCodeSerializer(serializers.ModelSerializer):
    Product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())

    class Meta:
        model = QRCode
        fields = ['id', 'qr_image', 'Product']


class DynamicQRCodeSerializer(serializers.ModelSerializer):
    qr_image_url = serializers.ImageField(source='qr_image',)  # Provide the URL to the QR image

    class Meta:
        model = QRCode
        fields = ['qr_image', 'data', 'qr_image_url']
        