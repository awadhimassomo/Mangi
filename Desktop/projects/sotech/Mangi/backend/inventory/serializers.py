#serializer the  data
from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from .models import Product,Supplier,Category,Transaction,Warehouse
from qcode.models import QRCode


class CategorySerializer(ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

class WarehouseSerializer(ModelSerializer):
    class Meta:
        model = Warehouse
        fields = '__all__'
        

class  SupplierSerializer(ModelSerializer):
    class Meta:
        model = Supplier
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

class ProductSerializer(ModelSerializer):
    supplier_name = serializers.CharField(source='Supplier.supplier_name',  read_only=True)
    WarehouseName = serializers.CharField(source='Warehouse.WarehouseName',  read_only=True)
    category_name= serializers.CharField(source='Category.category_name',  read_only=True)
    class Meta:
        model = Product
        fields = ['id','ProductName','Price','Cost','Quantity','DateCreated','DateUpdated','Supplier','Category','Barcode','supplier_name','WarehouseName','category_name']
        read_only_fields = ('created_at', 'updated_at')

# Transcation
class TransactionSerializer(ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')





