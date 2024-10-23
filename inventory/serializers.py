#serializer the  data
from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from .models import BusinessType, Expense, Installment, Order, OrderItem, Product, Sales, SalesItem,Supplier,Category,Transaction,Warehouse,Purchase



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

class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = [
            'id', 
            'supplierName', 
            'contactPerson', 
            'contactEmail',  
            'contactPhone', 
            'address', 
            'supplierType',  
            'business', 
            'isSynced', 
            'isDeleted'
        ]

    def to_internal_value(self, data):
        # Map incoming field names to the model field names
        data = {
            'id': data.get('id'),
            'supplierName': data.get('supplierName') or data.get('supplier_name'),
            'contactPerson': data.get('contactPerson') or data.get('contact_person'),
            'contactEmail': data.get('contactEmail') or data.get('contact_email'),
            'contactPhone': data.get('contactPhone'),
            'address': data.get('address'),
            'supplierType': data.get('supplierType') or data.get('supplier_type'),
            'business': data.get('business_id'),  
            'isSynced': data.get('isSynced'),
            'isDeleted': data.get('isDeleted'),
        }
        return super().to_internal_value(data)

    def validate_supplierType(self, value):
        # Normalize input to lowercase for comparison
        normalized_value = value.strip().lower()
        valid_choices = {choice[1].lower(): choice[0] for choice in Supplier.supplierType_CHOICES}

        if normalized_value in valid_choices:
            return valid_choices[normalized_value]  # Return the normalized value
        else:
            raise serializers.ValidationError(f"'{value}' is not a valid supplier type. Must be one of: {list(valid_choices.keys())}.")


class PurchaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Purchase
        fields = '__all__'


class BusinessTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessType
        fields = ['id', 'name']


class ExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expense
        fields = [
            'id', 'date', 'without_tax_cost', 'with_tax_cost', 
            'total', 'approval_status', 'receipt', 'vendor', 
            'payment_method', 'notes', 'business', 'category'
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
        fields = ['id', 'transaction_id', 'due_date', 'amount_due', 'amount_paid', 'reminder_sent', 'business', 'customer_name', 'customer_phoneNumber']
        

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
class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'  # Include all fields, including 'id'

    def create(self, validated_data):
        # Ensure the provided UUID is used without generating a new one
        return Transaction.objects.create(**validated_data)


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['product', 'quantity', 'unit_price', 'total_price']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)  # 'items' because of related_name in OrderItem

    class Meta:
        model = Order
        fields = ['order_number', 'supplier', 'business', 'order_date', 'status', 'delivery_date', 'notes', 'token', 'items']

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        order = Order.objects.create(**validated_data)

        for item_data in items_data:
            OrderItem.objects.create(order=order, **item_data)

        return order
    
class OrderItemSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField()
    unit_price = serializers.FloatField()
    total_price = serializers.FloatField()

    def validate(self, data):
        """
        Validate each order item data.
        """
        if data['quantity'] <= 0:
            raise serializers.ValidationError("Quantity must be greater than zero.")
        if data['unit_price'] <= 0:
            raise serializers.ValidationError("Unit price must be greater than zero.")
        return data


class CreateOrderSerializer(serializers.Serializer):
    order_number = serializers.CharField(max_length=50)
    supplier_id = serializers.UUIDField()
    business_id = serializers.IntegerField()
    items = OrderItemSerializer(many=True)

    def validate_items(self, value):
        """
        Ensure that there is at least one order item.
        """
        if not value:
            raise serializers.ValidationError("Order items cannot be empty.")
        return value

    def validate(self, data):
        """
        Additional validation can be added here if needed.
        """
        # For example, check if total order amount exceeds a certain limit
        return data


class SalesItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalesItem
        fields = ['sale', 'product', 'quantity', 'price_per_unit', 'total_price']
        read_only_fields = ['sale', 'total_price']



class SalesSerializer(serializers.ModelSerializer):
    # Define transaction_id field explicitly
    transaction_id = serializers.UUIDField(write_only=True)

    # Keep transaction details for the response
    transaction_details = serializers.SerializerMethodField(read_only=True)

    # Include details about the related business
    business_details = serializers.SerializerMethodField(read_only=True)

    # Serialize the related SalesItems (purchased products)
    items = SalesItemSerializer(many=True, read_only=True)

    class Meta:
        model = Sales
        fields = [
            'id', 'transaction_id', 'transaction_details', 'business', 'business_details', 
            'total_amount', 'isSynced', 'isDeleted', 'items'
        ]
        read_only_fields = ['isSynced', 'isDeleted', 'items', 'transaction_details', 'business_details']

    def get_transaction_details(self, obj):
        """ Returns details about the transaction """
        if obj.transaction_id:
            return {
                'transaction_id': obj.transaction_id.id,
                'date': obj.transaction_id.date,
                'description': obj.transaction_id.description
            }
        return None

    def get_business_details(self, obj):
        """ Returns details about the business """
        if obj.business:
            return {
                'business_id': obj.business.id,
                'name': obj.business.businessName,
                'phone': obj.business.businessPhoneNumber,
                'email': obj.business.businessEmail
            }
        return None

    


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


