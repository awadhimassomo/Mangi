#serializer the  data
from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from .models import Expense, Installment, Order, OrderItem, Product, Sales,Supplier,Category,Transaction,Warehouse,Purchase



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

class PurchaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Purchase
        fields = '__all__'






class ExpenseSerializer(serializers.ModelSerializer):
    categoryName = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Expense
        fields = [
            'id', 'date', 'categoryName', ' without_tax_cost', 
            'with_tax_cost', 'total', 'approval_status', 'receipt',
            'vendor', 'payment_method', 'notes', 'business'
        ]


class ProductSuggestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'product_name', 'price']


class InstallmentSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='transaction.customer.name', read_only=True)
    customer_phoneNumber = serializers.CharField(source='transaction.customer.phoneNumber', read_only=True)

    class Meta:
        model = Installment
        fields = ['id', 'transaction', 'due_date', 'amount_due', 'amount_paid', 'reminder_sent', 'business', 'customer_name', 'customer_phoneNumber']
        

class ProductSerializer(serializers.ModelSerializer):
    contact_phone = serializers.CharField(source='supplier.contactPhone', read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'product_name', 'price', 'cost', 'quantity', 'barcode', 
            'date_created', 'date_updated', 'supplier_id', 'category_id', 
            'warehouse_id', 'expire_date', 'active', 'description', 
            'taxable', 'product_type', 'discountable', 'business', 
            'min_stock', 'max_stock', 'location_type', 'location_identifier', 
            'isDeleted', 'isSynced', 'lastSyncTime', 'contact_phone'
        ]
    
    def create(self, validated_data):
        business = validated_data.pop('business')
        return Product.objects.create(business=business, **validated_data)
    
    def update(self, instance, validated_data):
        business = validated_data.pop('business', None)
        if business:
            instance.business = business
        return super().update(instance, validated_data)






# Transcation
class TransactionSerializer(ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class SalesSerializer(serializers.ModelSerializer):
    transaction = serializers.PrimaryKeyRelatedField(queryset=Transaction.objects.all())

    class Meta:
        model = Sales
        fields = '__all__'

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = '__all__'


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    payments = TransactionSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = '__all__'


