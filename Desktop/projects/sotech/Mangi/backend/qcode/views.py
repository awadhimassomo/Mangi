from django.shortcuts import render

from .models import QRCode
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from  inventory.models import Product
from .serializers import QRCodeSerializer
from inventory.serializers import ProductSerializer
from rest_framework.decorators import api_view
from rest_framework import generics




@api_view(['GET'])
def getRoutes(request):
    routes = [
        {
            'Endpoint': '/qcode/qrcode/create/',
            'method': 'POST',
            'body': {'data': 'string'},
            'description': 'Creates a new QR code with provided data.'
        },
        {
            'Endpoint': '/qcode/qrcodes/',
            'method': 'GET',
            'body': None,
            'description': 'Returns an array of all QR codes.'
        },
    ]
    return Response(routes)

@api_view(['GET'])
def getQCodes(request):
    qcodes = QRCode.objects.all()
    Product=Product.objects.all()
    serializer = QRCodeSerializer(qcodes, many=True)
    return Response(serializer.data)

# Create your views here.


class QRCodeAPIView(generics.CreateAPIView):
    
    serializer_class = QRCodeSerializer
    queryset = Product.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return QRCodeSerializer
        return ProductSerializer  # Use ProductSerializer for GET requests

    def get_queryset(self):
        if self.request.method == 'GET':
            return Product.objects.all() # Return products to choose from
        return super().get_queryset()  # Default to QRCode objects for POST

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs) # Call the default POST method
