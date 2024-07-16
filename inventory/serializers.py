#serializer the  data
from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from .models import Product,Supplier,Category,Transaction,Warehouse,Purchase
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
        

class PurchaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Purchase
        fields = '__all__'

class  SupplierSerializer(ModelSerializer):
    class Meta:
        model = Supplier
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')
        
class ProductSerializer(serializers.ModelSerializer):
    supplier_name = serializers.CharField(source='supplier.supplier_name', read_only=True)
    category_name = serializers.CharField(source='category.category_name', read_only=True)
    warehouse_name = serializers.CharField(source='warehouse.warehouse_name', read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'product_name', 'price', 'cost', 'quantity', 'date_created', 'date_updated', 
            'supplier', 'category', 'barcode', 'supplier_name', 'warehouse_name', 'category_name'
        ]
        read_only_fields = ('date_created', 'date_updated')

# Transcation
class TransactionSerializer(ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')





