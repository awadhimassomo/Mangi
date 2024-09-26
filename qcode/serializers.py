from rest_framework import serializers
from inventory.serializers import ProductSerializer
from .models import QRCode
from inventory.models import Product

#qrcode
class QRCodeSerializer(serializers.ModelSerializer):
    Product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())

    class Meta:
        model = QRCode
        fields = ['id', 'qrImage', 'Product']


class DynamicQRCodeSerializer(serializers.ModelSerializer):
    qrImage_url = serializers.ImageField(source='qrImage',)  # Provide the URL to the QR image

    class Meta:
        model = QRCode
        fields = ['qrImage', 'data', 'qrImage_url']
        