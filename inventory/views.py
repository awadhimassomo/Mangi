from datetime import date, timedelta, timezone
from decimal import ROUND_HALF_UP, Decimal
import random
import string
from venv import logger
from django.shortcuts import render
import requests
from rest_framework.decorators import api_view,permission_classes
from rest_framework.response import Response
from django.http import JsonResponse
from django.utils.crypto import get_random_string
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils.crypto import get_random_string
import logging  # For logging data received
from datetime import timedelta
logger = logging.getLogger(__name__)
from rest_framework import permissions


from sms.views import generate_reference
from .serializers import CreateOrderSerializer, ExpensePolicySerializer, ExpenseSerializer, InstallmentSerializer, OrderItemSerializer, ProductSerializer, ProductSuggestionSerializer, SalesSerializer,SupplierSerializer,CategorySerializer #ExpenseSerializer,
from .serializers import TransactionSerializer,WarehouseSerializer,PurchaseSerializer
from .models import BusinessType, Expense, ExpensePolicy, Installment, Order, OrderItem, Product, ProductBusinessTypeAssociation, PublicProduct, Sales, SalesItem,Supplier,Category,Transaction,Warehouse,Purchase
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework import status,viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework import filters
from rest_framework.generics  import ListAPIView
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from registration.models import Business, BusinessProfile, Customer
from django.views.decorators.http import require_GET
from django.shortcuts import get_object_or_404
from datetime import datetime
from django.db import transaction





@api_view(['GET'])
def getRoutes(request):
    routes =[

        {
            'Endpoint' : '/Products/',
            'method':'GET',
            'body':None,
            'description':'Return an array of products'
        },

        {
              'Endpoint' : '/Products/id',
            'method':'GET',
            'body':None,
            'description':'Return a single product'
        },
        {
          'Endpoint' : '/Products/Create',
            'method':'GET',
            'body':None,
            'description':'Return an array of products'
        },

        {
          'Endpoint' : '/Products/Create',
            'method':'POST',
            'body':{'Description':""},
            'description':'Create a product with data sent via post'
        },

         {
          'Endpoint' : '/Products/id/update/',
            'method':'PUT',
            'body':{'Description':""},
            'description':'Create a product with data sent via post'
        },
          {
          'Endpoint' : '/Products/id/delete/',
            'method':'DELETE',
            'body':None,
            'description':'Create a product with data sent via post'
        },
        #Supplier
        {
            'Endpoint' : '/Suppliers/',
            'method':'GET',
            'body':None,
            'description':'Return an array of suppliers'
        },
        {
              'Endpoint' : '/Suppliers/id',
            'method':'GET',
            'body':None,
            'description':'Return a single supplier'
        },
        {
          'Endpoint' : '/Suppliers/Create',
            'method':'GET',
            'body':None,
            'description':'Return an array of suppliers'
        },

        {
          'Endpoint' : '/Suppliers/Create',
            'method':'POST',
            'body':{'supplierName ':""},
            'description':'Create a supplier with data sent via post'
        },

         {
          'Endpoint' : '/Suppliers/id/update/',
            'method':'PUT',
            'body':{'supplierName ':""},
            'description':'Create a supplier with data sent via post'
        },
          {
          'Endpoint' : '/Suppliers/id/delete/',
            'method':'DELETE',
            'body':None,
            'description':'Create a supplier with data sent via post'
        },

        #Category
        {
            'Endpoint' : '/Categories/',
            'method':'GET',
            'body':None,
            'description':'Return an array of categories'
        },
        {
              'Endpoint' : '/Categories/id',
            'method':'GET',
            'body':None,
            'description':'Return a single category'
        },
        {
          'Endpoint' : '/Categories/Create',
            'method':'GET',
            'body':None,
            'description':'Return an array of categories'
        },

        {
          'Endpoint' : '/Categories/Create',
            'method':'POST',
            'body':{'category_name':""},
            'description':'Create a category with data sent via post'
        },

         {
          'Endpoint' : '/Categories/id/update/',
            'method':'PUT',
            'body':{'category_name':""},
            'description':'Create a category with data sent via post'
        },
          {
          'Endpoint' : '/Categories/id/delete/',
            'method':'DELETE',
            'body':None,
            'description':'Create a category with data sent via post'
        },
        #Warehouse
        {
            'Endpoint' : '/Warehouses/',
            'method':'GET',
            'body':None,
            'description':'Return an array of warehouses'
        },
        {
              'Endpoint' : '/Warehouses/id',
            'method':'GET',
            'body':None,
            'description':'Return a single warehouse'
        },
        {
          'Endpoint' : '/Warehouses/Create',
            'method':'GET',
            'body':None,
            'description':'Return an array of warehouses'
        },

        {
          'Endpoint' : '/Warehouses/Create',
            'method':'POST',
            'body':{'warehouseName':""},
            'description':'Create a warehouse with data sent via post'
        },

         {
          'Endpoint' : '/Warehouses/id/update/',
            'method':'PUT',
            'body':{'warehouseName':""},
            'description':'Create a warehouse with data sent via post'
        },
          {
          'Endpoint' : '/Warehouses/id/delete/',
            'method':'DELETE',
            'body':None,
            'description':'Create a warehouse with data sent via post'
        },

    ]

    return Response(routes)

#order notifcation system and views: 

class NotifySupplierAPIView(APIView):
    def post(self, request):
        supplier_id = request.data.get('supplier_id')
        product_name = request.data.get('product_name')
        quantity_needed = request.data.get('quantity_needed')
        user = request.data.get('user')

        # Implement logic to notify the supplier, e.g., send an email, SMS, or push notification
        # For now, we'll just simulate this by printing to the console
        print(f"Notification to Supplier {supplier_id}: User {user} is low on {product_name} (needs {quantity_needed} units).")

        # Return a success response
        return Response({'message': 'Supplier notified successfully'}, status=status.HTTP_200_OK)
    
class PreOrderNotificationAPIView(APIView):
    def post(self, request):
        # Extract the pre-order data from the request
        preorder_id = request.data.get('preorder_id')
        product_name = request.data.get('product_name')
        quantity_needed = request.data.get('quantity_needed')

        # Prepare the response data
        response_data = {
            'preorder_id': preorder_id,
            'product_name': product_name,
            'quantity_needed': quantity_needed,
            'message': 'Pre-order created due to low stock. Please review and confirm.'
        }

        # Send the response back to the frontend
        return Response(response_data, status=status.HTTP_200_OK)



class CreateOrderAPIView(APIView):
    
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        # Log the received data
        logger.info(f"Received order data: {request.data}")
        
        # Deserialize and validate the request data
        serializer = CreateOrderSerializer(data=request.data)
        if not serializer.is_valid():
            logger.error(f"Invalid data received: {serializer.errors}")
            return Response({'status': 'error', 'message': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        order_number = data.get('order_number')
        supplier_id = data.get('supplier_id')
        business_id = data.get('business_id')
        order_items = data.get('items', [])

        try:
            # Fetch supplier and business from the database
            supplier = Supplier.objects.get(id=supplier_id)
            business = Business.objects.get(id=business_id)
            
            # Create the order
            order = self._create_order(order_number, supplier, business)
            
            # Process the order items
            self._create_order_items(order, order_items)
            
            # Generate a unique token and save it to the order
            self._generate_order_token(order)

            # Send SMS notification to the supplier
            self._send_order_notification(supplier, order_number, order_items, order.token)

            logger.info(f"Order {order_number} created successfully.")
            return Response({'status': 'success', 'message': 'Order created and notifications sent.'}, status=status.HTTP_201_CREATED)
        
        except Supplier.DoesNotExist:
            logger.error("Supplier not found.")
            return Response({'status': 'error', 'message': 'Supplier not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        except Business.DoesNotExist:
            logger.error("Business not found.")
            return Response({'status': 'error', 'message': 'Business not found.'}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            # Catch any other exception and log it
            logger.error(f"Error creating order: {e}")
            return Response({'status': 'error', 'message': 'An unexpected error occurred while creating the order.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _create_order(self, order_number, supplier, business):
        """
        Creates and returns an order instance.
        """
        order = Order.objects.create(
            order_number=order_number,
            supplier=supplier,
            business=business
        )
        return order

    def _create_order_items(self, order, items):
        """
        Creates order items for the given order.
        """
        for item_data in items:
            product_id = item_data.get('product_id')
            quantity = item_data.get('quantity')
            unit_price = item_data.get('unit_price')

            # Calculate total price
            total_price = quantity * unit_price
            
            # Create and validate the order item
            item_serializer = OrderItemSerializer(data={
                'order': order.id,
                'product_id': product_id,
                'quantity': quantity,
                'unit_price': unit_price,
                'total_price': total_price
            })
            if item_serializer.is_valid():
                item_serializer.save()
            else:
                logger.error(f"Invalid order item data: {item_serializer.errors}")
                raise ValueError(f"Invalid order item data: {item_serializer.errors}")

    def _generate_order_token(self, order):
        """
        Generates a unique token for the order and saves it.
        """
        token = get_random_string(length=32)
        order.token = token
        order.save()

    def _send_order_notification(self, supplier, order_number, order_items, token):
        """
        Sends an SMS notification to the supplier.
        """
        order_link = f"https://yourwebsite.com/complete_order/{token}/"
        send_order_notification_via_sms(
            supplier.contactPhone,
            order_number,
            order_items,
            order_link
        )

    
def fetch_product_name(product_id):
    try:
        # Fetch the product from the database using the product_id
        product = Product.objects.get(id=product_id)
        return product.product_name
    except Product.DoesNotExist:
        return "Unknown Product"

def send_order_notification_via_sms(phone_number, order_number, order_items, order_link):
    try:
        from_ = "SOTECH"  # Sender name
        url = 'https://messaging-service.co.tz/api/sms/v1/text/single'
        headers = {
            'Authorization': "Basic YXRoaW06TWFtYXNob2tv", 
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        reference = generate_reference()  # Generate a reference for the message

        # Generate the ordered items list as text for the SMS, fetching product names from the database
        items_text = "\n".join([
            f"{item['quantity']} x {fetch_product_name(item['product_id'])} @ {item['unit_price']} Tsh" 
            for item in order_items
        ])

        # Message content with order link
        message = f"Your order {order_number} has been created.\nItems:\n{items_text}\nComplete the order here: {order_link}"

        payload = {
            "from": from_,
            "to": phone_number,
            "text": message,
            "reference": reference,
        }

        # Logging for tracking the request
        print(f"Sending order notification to: {phone_number}, Reference: {reference}")

        response = requests.post(url, headers=headers, json=payload)

        if response.status_code == 200:
            print("Order notification message sent successfully!")
            return True
        else:
            print("Failed to send order notification message.")
            print(response.status_code)
            print(response.text)
            return False
    except Exception as e:
        print(f'Error sending order notification: {e}')
        return False    

def process_order(request, token):
    order = get_object_or_404(Order, token=token)
    # Update the order status to "Processing"
    order.status = 'Processing'
    order.save()
    return Response({'status': 'success', 'message': 'Order is being processed.', 'order_status': order.status}, status=status.HTTP_200_OK)

def cancel_order(request, token):
    order = get_object_or_404(Order, token=token)
    # Update the order status to "Cancelled"
    order.status = 'Cancelled'
    order.save()
    return Response({'status': 'success', 'message': 'Order has been cancelled.', 'order_status': order.status}, status=status.HTTP_200_OK)

def send_order(request, token):
    order = get_object_or_404(Order, token=token)
    # Update the order status to "Sent"
    order.status = 'Sent'
    order.save()
    return Response({'status': 'success', 'message': 'Order has been sent.', 'order_status': order.status}, status=status.HTTP_200_OK)

def complete_order_view(request, token):
    # Find the order with the given token
    order = get_object_or_404(Order, token=token)

    # Pass the order details to the template
    return render(request, 'complete_order.html', {'order': order})
        

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getProducts(request):
    user = request.user
    print(f"Authenticated user: {user}")  # This should print the authenticated user's information

    if not request.user.is_authenticated:
        return Response({"error": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)

    business_id = request.query_params.get('business_id')

    if not business_id:
        return Response({"error": "business_id parameter is required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        business = Business.objects.get(id=business_id, owner=user)  # Ensure the business belongs to the authenticated user
    except Business.DoesNotExist:
        return Response({"error": "Business not found or not owned by the user"}, status=status.HTTP_404_NOT_FOUND)

    products = Product.objects.filter(business=business)
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def  getNote(request,pk):
    product=Product.objects.all()
    serializer=ProductSerializer(product,many=False)
    return Response(serializer.data)

@api_view(['PUT', 'PATCH'])
def updateProduct(request, pk):
    try:
        # Ensure 'pk' is correctly provided and is an integer
        if not pk.isdigit():
            return Response({'error': 'Invalid product ID'}, status=status.HTTP_400_BAD_REQUEST)

        product = Product.objects.get(id=int(pk))

        # Extract data from the request
        data = request.data

        # Log request data
        print("Request Dataa:", data)

        # Validate and update only provided fields
        if 'quantity' in data:
            product.quantity = data['quantity']

        # Optional fields
        if 'product_name' in data:
            product.product_name = data['product_name']
        if 'price' in data:
            product.price = data['price']
        if 'cost' in data:
            product.cost = data['cost']
        if 'barcode' in data:
            product.barcode = data['barcode']

        # Optional related fields validation
        if 'supplier_id' in data:
            try:
                product.supplier = Supplier.objects.get(id=data['supplier_id'])
            except Supplier.DoesNotExist:
                return Response({'error': 'Supplier nott found'}, status=status.HTTP_404_NOT_FOUND)
        if 'category_id' in data:
            try:
                product.category = Category.objects.get(id=data['category_id'])
            except Category.DoesNotExist:
                return Response({'error': 'Category not found'}, status=status.HTTP_404_NOT_FOUND)
        if 'warehouse_id' in data:
            try:
                product.warehouse = Warehouse.objects.get(id=data['warehouse_id'])
            except Warehouse.DoesNotExist:
                return Response({'error': 'Warehouse not found'}, status=status.HTTP_404_NOT_FOUND)

        product.save()

        # Return the serialized product data
        serializer = ProductSerializer(product)
        return Response(serializer.data, status=status.HTTP_200_OK)

    except Product.DoesNotExist:
        return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        error_message = f'Error updating product: {str(e)}'
        print(error_message)
        return Response({'error': error_message}, status=status.HTTP_400_BAD_REQUEST)


# Product viesets

class CreateProduct(generics.CreateAPIView):
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]  # Ensure the user is authenticated

    def create(self, request, *args, **kwargs):
        # Ensure that the user is authenticated
        user = request.user

        # Extract product data from the request
        product_data = {
            'product_name': request.data.get('product_name'),
            'barcode': request.data.get('barcode'),
            'price': request.data.get('price'),
            'cost': request.data.get('cost'),
            'quantity': request.data.get('quantity'),
            'supplier_id': request.data.get('supplier_id'),
            'warehouse_id': request.data.get('warehouse_id'),
            'category_id': request.data.get('category_id'),
            'business_id': request.data.get('business_id'),
            'min_stock': request.data.get('min_stock'),  # New field
            'max_stock': request.data.get('max_stock'),  # New field
            'expire_date': request.data.get('expire_date'),  # New field
            'location_type': request.data.get('location_type'),  # New field
            'location_identifier': request.data.get('location_identifier'),
            'contactPhone':request.data.get('contactPhone')  ,# New field
        }

        # Log request data
        logger.info(f"Request Data: {product_data}")

        # Mandatory field validations excluding barcode and other optional fields
        missing_fields = [field for field in ['product_name', 'price', 'cost', 'quantity', 'category_id'] if not product_data.get(field)]
        if missing_fields:
            error_message = f'Missing fields: {", ".join(missing_fields)}'
            logger.error(error_message)
            return Response({'error': error_message}, status=status.HTTP_400_BAD_REQUEST)

        # Validate related objects by ID
        errors = []
        supplier, category, warehouse = None, None, None
# Validate supplier by phone number instead of ID
        contact_phone = product_data.get('contactPhone')
        if contact_phone:
            try:
                supplier = Supplier.objects.get(contactPhone=contact_phone)

                # **Updated Section**: Compare local and remote supplier IDs
                local_id = str(supplier.id).strip()
                remote_id = str(product_data.get('supplier_id')).strip()

                if local_id != remote_id:
                    logger.error(f"Supplier ID mismatch: Local ID {repr(local_id)}, Remote ID {repr(remote_id)}")
                else:
                    logger.info(f"Supplier ID match: {local_id}")

            except Supplier.DoesNotExist:
                errors.append('Supplier not found')
        else:
            errors.append('Contact phone is missing in the request data.')
            
# Validate category and ensure subtype is unique
        if product_data.get('category_id'):
             try:
        # Fetch category by ID
                category = Category.objects.get(id=product_data['category_id'])
                logger.info(f"Category found: {category.id}")  # Log category ID

        # Validate that the subtype is provided
                if 'subtype' in product_data:
                     subtype = product_data['subtype']

            # Check if the subtype exists within another category
                     if Category.objects.filter(subtype=subtype).exclude(id=category.id).exists():
                          errors.append(f"Subtype '{subtype}' already exists within another category")
                     else:
                         logger.info(f"Subtype '{subtype}' is unique.")

             except Category.DoesNotExist:
                  errors.append('Category not found')
                  logger.error("Category not found for ID: {}".format(product_data['category_id']))





        # Validate warehouse
        if product_data['warehouse_id']:
            try:
                warehouse = Warehouse.objects.get(id=product_data['warehouse_id'])
                logger.info(f"Warehouse found: {warehouse.id}")  # Log warehouse ID (if exists)
            except Warehouse.DoesNotExist:
                errors.append('Warehouse not found')

        if errors:
            error_message = f'Errors: {", ".join(errors)}'
            logger.error(error_message)
            return Response({'errors': errors}, status=status.HTTP_404_NOT_FOUND)

        # Check if the business belongs to the authenticated user
        business_id = product_data.get('business_id')
        try:
            business = Business.objects.get(id=business_id, owner=user)
            logger.info(f"Business found: {business.id}")  # Log business ID
        except Business.DoesNotExist:
            raise PermissionDenied("Business not found or not owned by the user.")

        # Parse and validate expire_date
        if product_data['expire_date']:
            try:
                product_data['expire_date'] = datetime.strptime(product_data['expire_date'], '%Y-%m-%d').date()
            except ValueError:
                return Response({'error': 'Invalid expire_date format. Expected YYYY-MM-DD.'}, status=status.HTTP_400_BAD_REQUEST)

        # Ensure non-negative values for price, cost, and quantity

        # Creating the product with new fields
        try:
            new_product = Product.objects.create(
                product_name=product_data['product_name'],
                price=product_data['price'],
                cost=product_data['cost'],
                quantity=product_data['quantity'],
                supplier=supplier,
                warehouse=warehouse,
                category=category,
                business=business,  # Use the validated business instance
                barcode=product_data.get('barcode', None),  # Allow empty barcode
                min_stock=product_data.get('min_stock', 0),  # Default to 0 if not provided
                max_stock=product_data.get('max_stock', 0),  # Default to 0 if not provided
                expire_date=product_data.get('expire_date', None),  # None if not provided
                location_type=product_data.get('location_type', 'store'),  # Default to 'store'
                location_identifier=product_data.get('location_identifier', None),  # None if not provided
            )
  
            
        except Exception as e:
            error_message = f'Error creating productt: {str(e)}'
            logger.error(error_message)
            return Response({'error': error_message}, status=status.HTTP_400_BAD_REQUEST)

        # Return the serialized product data
        serializer = self.get_serializer(new_product)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class SyncProductsView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        client_products = request.data.get('products', [])
        business_id = request.data.get('business_id')
        
        logger.info(f"Received sync request from {user.username}")
        logger.info(f"Request data: {request.data}")

        if not client_products:
            logger.warning("No products found in the request.")
            return Response({'message': 'No products to sync'}, status=status.HTTP_400_BAD_REQUEST)

        # Ensure business_id is provided
        try:
            business = Business.objects.get(id=business_id, owner=user)
        except Business.DoesNotExist:
            logger.error(f"Business ID {business_id} not found or not owned by the user")
            return Response({"error": f"Business ID {business_id} not found or not owned by the user"}, status=status.HTTP_404_NOT_FOUND)

        synced_products = []
        
        for product_data in client_products:
            logger.info(f"Processing product for business_id: {business_id}")

            # Assign the business to the product data
            product_data['business'] = business.id

            product = Product.objects.filter(barcode=product_data['barcode'], business=business).first()

            if product:
                logger.info(f"Updating existing product: {product.product_name}")
                # Update product directly
                product_serializer = ProductSerializer(product, data=product_data, partial=True)
                if product_serializer.is_valid():
                    product = product_serializer.save()  # Save the updated product
                else:
                    logger.error(f"Error updating product: {product_serializer.errors}")
                    return Response(product_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                logger.info(f"Creating new product: {product_data.get('product_name')}")
                product_serializer = ProductSerializer(data=product_data)
                if product_serializer.is_valid():
                    product = product_serializer.save()  # Save the new product
                else:
                    logger.error(f"Error creating product: {product_serializer.errors}")
                    return Response(product_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            # Sync product to PublicProduct only if creation/update was successful
            self._sync_to_public_product(product, product_data)

            synced_products.append(product_serializer.data)  # Collect synced data

        logger.info(f"Returning synced products: {synced_products}")
        return Response({
            'synced_products': synced_products,
        }, status=status.HTTP_200_OK)

    def _sync_to_public_product(self, product, product_data):
        try:
            # Check if the public product already exists
            public_product, created = PublicProduct.objects.get_or_create(
                barcode=product.barcode,
                defaults={
                    'product_name': product.product_name,
                    # other fields as needed
                }
            )
            if not created:
                # Update public product if it already exists
                public_product.product_name = product.product_name
                # other fields as needed
                public_product.save()

            # Create or update association
            ProductBusinessTypeAssociation.objects.update_or_create(
                product=product,
                public_product=public_product,
                defaults={'business_type': product.business.businessType}
            )
            logger.info(f"Successfully synced product {product.product_name} to PublicProduct")
        except Exception as e:
            logger.error(f"Error syncing product to PublicProduct: {str(e)}")



@api_view(['DELETE'])
def deleteProduct(request, pk):
    try:
        # Print the product details before deleting
        product = Product.objects.get(id=pk)
        print(f"Deleting Product: {product}")  # This will print the product object
        
        # Optionally, print all products in the database
        all_products = Product.objects.all()
        print("All Products in Database:")
        for p in all_products:
            print(f"ID: {p.id}, Name: {p.product_name}, Price: {p.price}")  # Adjust fields based on your model
        
        # Delete the product
        product.delete()
        
        return Response("Product was deleted", status=status.HTTP_200_OK)
    
    except Product.DoesNotExist:
        return Response("Product not found", status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getSuppliers(request):
    user = request.user  # Get the authenticated user
    business_id = request.query_params.get('business_id')  # Get the business ID from the query parameters

    # Check if business_id is provided
    if not business_id:
        return Response({"error": "business_id parameter is required"}, status=status.HTTP_400_BAD_REQUEST)

    # Ensure the business belongs to the authenticated user
    try:
        business = Business.objects.get(id=business_id, owner=user)
    except Business.DoesNotExist:
        return Response({"error": "Business not found or not owned by the user"}, status=status.HTTP_404_NOT_FOUND)

    # Fetch suppliers associated with the business
    suppliers = Supplier.objects.filter(business=business)
    serializer = SupplierSerializer(suppliers, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def createSupplier(request):
    # Ensure the user is authenticated
    if not request.user.is_authenticated:
        return Response({"error": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)

    user = request.user  # Get the authenticated user
    business_id = request.data.get('business_id')  # Get the business ID from the request data

    if not business_id:
        return Response({"error": "Business ID is required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Ensure the business belongs to the authenticated user
        business = Business.objects.get(id=business_id, owner=user)
    except Business.DoesNotExist:
        return Response({"error": "Business not found or not owned by the user"}, status=status.HTTP_404_NOT_FOUND)
    except Business.MultipleObjectsReturned:
        return Response({"error": "Multiple businesses found. Please specify a unique business ID."}, status=status.HTTP_400_BAD_REQUEST)

    # Log the incoming supplier data
    logger.info(f"Incoming supplier data: {request.data}")

    # Include the business in the supplier data
    supplier_data = request.data.copy()
    supplier_data['business'] = business.id

    # Wrap the database save operation in an atomic transaction
    try:
        with transaction.atomic():
            serializer = SupplierSerializer(data=supplier_data)
            if serializer.is_valid():
                supplier = serializer.save()
                
                # Log the successful creation of the supplier
                logger.info(f"Supplier created successfully: {supplier}")
                
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                # Log validation errors
                logger.error(f"Validation errors: {serializer.errors}")
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        # Log any unexpected errors
        logger.error(f"An unexpected error occurred: {str(e)}")
        return Response({"error": "An unexpected error occurred."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def updateSupplier(request, pk):
    user = request.user  # Get the authenticated user
    business_id = request.data.get('business_id')  # Get the business ID from the request data

    if not business_id:
        return Response({"error": "Business ID is required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Ensure the supplier belongs to the business owned by the authenticated user
        supplier = Supplier.objects.get(id=pk, business_id=business_id, business__owner=user)
    except Supplier.DoesNotExist:
        return Response({"error": "Supplier no found or not associated with your business"}, status=status.HTTP_404_NOT_FOUND)

    serializer = SupplierSerializer(instance=supplier, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def deleteSupplier(request, pk):
    user = request.user  # Get the authenticated user

    # Check for business_id in query parameters
    business_id = request.query_params.get('business_id')
    if not business_id:
        logger.error("Business ID is missing in request from user %s", user.username)
        return Response({"error": "Business ID is required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Ensure the supplier belongs to the business owned by the authenticated user
        supplier = Supplier.objects.get(id=pk, business_id=business_id, business__owner=user)
    except Supplier.DoesNotExist:
        logger.warning("Supplier with id %s not found or not associated with business ID %s for user %s", pk, business_id, user.username)
        return Response({"error": "Supplier on found or not associated with your business."}, status=status.HTTP_404_NOT_FOUND)
    except Supplier.MultipleObjectsReturned:
        logger.error("Multiple suppliers found with the same ID %s, which is unexpected.", pk)
        return Response({"error": "Multiple suppliers found with the same ID, which is unexpected."}, status=status.HTTP_400_BAD_REQUEST)
    except ValueError:
        logger.error("Invalid ID format provided: %s", pk)
        return Response({"error": "Invalid ID format provided."}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.exception("Unexpected error occurred while retrieving supplier with ID %s for user %s: %s", pk, user.username, str(e))
        return Response({"error": "An unexpected error occurred.", "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    try:
        supplier.delete()
        logger.info("Supplier with id %s deleted successfully for business ID %s by user %s", pk, business_id, user.username)
        return Response({"message": "Supplier was deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
    except Exception as e:
        logger.exception("Error during deletion of supplier with ID %s: %s", pk, str(e))
        return Response({"error": "Failed to delete the supplier.", "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SyncSupplierView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SupplierSerializer

    def post(self, request, *args, **kwargs):
        suppliers_data = request.data  # Get the supplier data from the request
        synced_suppliers = []
        errors = []

        # Log the incoming supplier data for debugging
        logger.info(f"Incoming supplier data: {suppliers_data}")

        # Handle both list and single dictionary
        if isinstance(suppliers_data, dict):
            suppliers_data = [suppliers_data]  # Wrap in a list if it's a single supplier

        if not isinstance(suppliers_data, list):
            logger.error("Expected a list of suppliers or a single supplier object.")
            return Response({"error": "Expected a list of suppliers or a single supplier object."}, status=status.HTTP_400_BAD_REQUEST)

        for supplier_data in suppliers_data:
            if not isinstance(supplier_data, dict):
                errors.append("Supplier data must be a dictionary.")
                continue

            supplier_id = supplier_data.get('id', None)  # Get the supplier ID from the data

            if not supplier_id:
                errors.append("Supplier data must contain an 'id' field.")
                continue

            # Check if the supplier already exists using the local ID
            try:
                supplier = Supplier.objects.get(id=supplier_id)  # Attempt to retrieve the supplier by ID
            except Supplier.DoesNotExist:
                supplier = None  # Supplier doesn't exist, will create a new one

            # Normalize supplierType: Check for both possible keys
            supplier_type = supplier_data.get('supplierType') or supplier_data.get('supplier_type', '').lower()
            valid_choices = {choice[1].lower(): choice[0] for choice in Supplier.supplierType_CHOICES}
            normalized_type = valid_choices.get(supplier_type)

            if normalized_type:
                supplier_data['supplierType'] = normalized_type  # Update to the model's stored value
            else:
                errors.append(f"Invalid supplierType: {supplier_type}. Must be one of: {list(valid_choices.keys())}")
                continue

            # Use the serializer to either update an existing supplier or create a new one
            serializer = self.get_serializer(instance=supplier, data=supplier_data, partial=True)  # Use partial=True to allow for updates

            # Validate the data
            if not serializer.is_valid():
                errors.append(f"Validation errors for supplier {supplier_id}: {serializer.errors}")
                continue

            supplier = serializer.save()  # Save the supplier to the database
            supplier.isSynced = True  # Mark as synced
            supplier.save()

            synced_suppliers.append(supplier.id)
            logger.info(f"Successfully synced supplier: {supplier.id}")

        if errors:
            return Response({"synced_suppliers": synced_suppliers, "errors": errors}, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            'synced_suppliers': synced_suppliers,
            'errors': errors
        }, status=status.HTTP_200_OK)


# Views for the Category model

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getCategories(request):
    user = request.user  # Get the authenticated user
    business_id = request.query_params.get('business_id')  # Get the business ID from query parameters

    # Check if business_id is provided
    if not business_id:
        return Response({"error": "business_id query parameter is required"}, status=400)

    # Ensure the business belongs to the authenticated user
    try:
        business = Business.objects.get(id=business_id, owner=user)
    except Business.DoesNotExist:
        return Response({"error": "Business not found or not owned by the user"}, status=404)

    # Fetch categories associated with the business
    categories = Category.objects.filter(business=business)
    serializer = CategorySerializer(categories, many=True)
    return Response(serializer.data)



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def createCategory(request):
    if not request.user.is_authenticated:
        return Response({"error": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)

    user = request.user
    business_id = request.data.get('business_id')

    if not business_id:
        return Response({"error": "Business ID is required"}, status=status.HTTP_400_BAD_REQUEST)

    # Fetch the specific business using the provided business_id
    try:
        business = Business.objects.get(id=business_id, owner=user)
    except Business.DoesNotExist:
        return Response({"error": "Business not found"}, status=status.HTTP_404_NOT_FOUND)
    except Business.MultipleObjectsReturned:
        return Response({"error": "Multiple businesses found. Please specify a unique business ID."}, status=status.HTTP_400_BAD_REQUEST)

    # Copy request data and add business_id
    data = request.data.copy()
    data['business'] = business.id

    serializer = CategorySerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def updateCategory(request, pk):
    user = request.user  # Get the authenticated user
    business_id = request.data.get('business_id')  # Get the business ID from the request data

    if not business_id:
        return Response({"error": "Business ID is required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Ensure the category belongs to the business owned by the authenticated user
        category = Category.objects.get(id=pk, business_id=business_id, business__owner=user)
    except Category.DoesNotExist:
        return Response({"error": "Category not found or not associated with your business"}, status=status.HTTP_404_NOT_FOUND)

    serializer = CategorySerializer(instance=category, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def deleteCategory(request, pk):
    user = request.user  # Get the authenticated user
    business_id = request.data.get('business_id')  # Get the business ID from the request data

    if not business_id:
        return Response({"error": "Business ID is required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Ensure the category belongs to the business owned by the authenticated user
        category = Category.objects.get(id=pk, business_id=business_id, business__owner=user)
    except Category.DoesNotExist:
        return Response({"error": "Category not found or not associated with your business"}, status=status.HTTP_404_NOT_FOUND)

    category.delete()
    return Response({"message": "Category was deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

# Views for the Transaction model
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getTransactions(request):
    user = request.user  # Get the authenticated user
    business_id = request.query_params.get('business_id')  # Get the business ID from query parameters

    if not business_id:
        return Response({"error": "Business ID is required"}, status=status.HTTP_400_BAD_REQUEST)

    # Filter transactions based on the business ID and ensure the business belongs to the authenticated user
    transactions = Transaction.objects.filter(business_id=business_id, business__owner=user)

    serializer = TransactionSerializer(transactions, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def createTransaction(request):
    data = request.data

    # Log the incoming data
    logger.info(f"Received transaction data: {data}")

    # Ensure transaction_type is lowercase
    if 'transaction_type' in data:
        data['transaction_type'] = data['transaction_type'].lower()
    else:
        logger.warning("Transaction type is missing in the request data.")

    # Ensure foreign keys exist
    business_id = data.get('business')
    customer_id = data.get('customer', None)
    supplier_id = data.get('supplier', None)  # If applicable

    # Validate business
    try:
        business = Business.objects.get(id=business_id)
    except Business.DoesNotExist:
        logger.error(f"Business with ID {business_id} does not exist.")
        return Response(
            {'error': f"Business with ID {business_id} does not exist."},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Validate customer or supplier
    if customer_id:
        try:
            customer = Customer.objects.get(id=customer_id)
        except Customer.DoesNotExist:
            logger.error(f"Customer with ID {customer_id} does not exist.")
            return Response(
                {'error': f"Customer with ID {customer_id} does not exist."},
                status=status.HTTP_400_BAD_REQUEST
            )
    elif supplier_id:
        try:
            supplier = Supplier.objects.get(id=supplier_id)
        except Supplier.DoesNotExist:
            logger.error(f"Supplier with ID {supplier_id} does not exist.")
            return Response(
                {'error': f"Supplier with ID {supplier_id} does not exist."},
                status=status.HTTP_400_BAD_REQUEST
            )

    # Log the modified data
    logger.debug(f"Modified transaction data: {data}")

    # Validate and save the transaction
    serializer = TransactionSerializer(data=data)
    if serializer.is_valid():
        try:
            transaction = serializer.save()  # Save the transaction
            logger.info(f"Transaction saved successfully: {serializer.data}")

            # Handle installments automatically if the transaction type is 'loan'
            if transaction.transaction_type == 'loan':
                num_installments = 3  # For example, split into 3 installments
                installment_amount = round(transaction.total_amount / num_installments, 2)  # Round to 2 decimal places
                installment_dates = [
                    transaction.transaction_date + timedelta(days=30 * i)
                    for i in range(1, num_installments + 1)
                ]
                
                installments_data = []
                for due_date in installment_dates:
                    installment_data = {
                        'due_date': due_date,
                        'amount_due': installment_amount,  # Ensure amount is rounded
                        'amount_paid': 0,
                        'business': transaction.business.id,
                        'transaction_id': transaction.id,
                        'customer': transaction.customer.id if transaction.customer else None,  # Add customer if present
                        'supplier': None  # You can add supplier if necessary
                    }

                    # Ensure that either customer or supplier is set
                    if not installment_data.get('customer') and not installment_data.get('supplier'):
                        logger.error("Either customer or supplier must be set for each installment.")
                        return Response(
                            {'error': 'Either customer or supplier must be set for each installment.'},
                            status=status.HTTP_400_BAD_REQUEST
                        )

                    installments_data.append(installment_data)
                    logger.debug(f"Generated installment data: {installment_data}")

                    # Serialize and save the installment data
                    installment_serializer = InstallmentSerializer(data=installment_data)

                    if installment_serializer.is_valid():
                        installment_serializer.save()
                        logger.info(f"Installment saved successfully: {installment_serializer.data}")
                    else:
                        logger.error(f"Installment validation errors: {installment_serializer.errors}")
                        return Response(installment_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error(f"Error saving transaction: {e}", exc_info=True)
            return Response(
                {'error': 'Failed to save transaction', 'details': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    else:
        # Log validation errors if the transaction fails to validate
        logger.error(f"Transaction validation errors: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class SyncTransactionView(APIView):
    def post(self, request, *args, **kwargs):
        # Log incoming request data
        logging.info(f"Incoming request data: {request.data}")

        # Check if the request data is empty or missing fields
        if not request.data:
            logging.warning("Request data is missing or empty.")
            return Response({'error': 'Request data is missing or empty.'}, status=status.HTTP_400_BAD_REQUEST)

        # Normalize the transaction type to be case insensitive
        if 'transaction_type' in request.data:
            request.data['transaction_type'] = request.data['transaction_type'].lower()

        # Convert transaction_date to the correct format if needed
        if 'transaction_date' in request.data:
            try:
                request.data['transaction_date'] = request.data['transaction_date'].strftime('%Y-%m-%d')
            except AttributeError:
                logging.warning("transaction_date is not in datetime format.")

        # Deserialize the request data
        serializer = TransactionSerializer(data=request.data)
        if serializer.is_valid():
            try:
                # Save the transaction to the database
                transaction = serializer.save()
                # Mark transaction as synced
                transaction.is_synced = True
                transaction.save()
                return Response({'message': 'Transaction synced successfully'}, status=status.HTTP_201_CREATED)
            except Exception as e:
                logging.error(f"Error saving transaction: {str(e)}")
                return Response({'error': 'Internal server error while saving transaction'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            # Log the errors to help understand the issue
            logging.warning(f"Invalid transaction data: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        
def generateInstallmentsForTransaction(transaction):
    installments_data = []
    num_installments = 3
    total_amount = Decimal(transaction.total_amount)
    installment_amount = (total_amount / num_installments).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)  # Rounds to 2 decimal places

    for i in range(num_installments):
        if installment_amount > Decimal('99999999.99'):
            installment_amount = Decimal('99999999.99')  # Ensure it doesn't exceed the max allowed value

        installment_data = {
            'amount_due': installment_amount,
            'due_date': (transaction.transaction_date + timedelta(days=30*(i+1))).strftime('%Y-%m-%d'),
            'business_id': transaction.business.id,
        }
        installments_data.append(installment_data)

    return installments_data


@api_view(['POST'])
def create_installment(request):
    print(f"Received data: {request.data}")  # Log the incoming data for debugging
    serializer = InstallmentSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    else:
        # Log the validation errors to understand what went wrong
        print(f"Validation errors: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)






class InstallmentListView(generics.ListAPIView):
    serializer_class = InstallmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Filter installments by business ID, passed as a query parameter
        business_id = self.request.query_params.get('business_id')
        return Installment.objects.filter(business_id=business_id)
    

#Expenses



@api_view(['PUT'])
def updateTransaction(request, pk):
    transaction = Transaction.objects.get(id=pk)
    serializer = TransactionSerializer(instance=transaction, data=request.data)
    if serializer.is_valid():
        serializer.save()
    return Response(serializer.data)

@api_view(['DELETE'])
def deleteTransaction(request, pk):
    transaction = Transaction.objects.get(id=pk)
    transaction.delete()
    return Response("Transaction was deleted")

#Create warehouse view

@api_view(['POST'])
@permission_classes([IsAuthenticated])  # Ensure the request is authenticated
def CreateWarehouses(request):
    try:
        data = request.data
        business_id = data.get('business_id')

        if not business_id:
            return Response({"error": "Business ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Ensure the business belongs to the authenticated user
        business = get_object_or_404(Business, id=business_id, owner=request.user)

        # Create the warehouse instance
        new_warehouse = Warehouse.objects.create(
            warehouseName=data['warehouseName'],
            warehouseLocation=data['warehouseLocation'],
            business=business
        )

        return Response({
            'id': new_warehouse.id,
            'warehouseName': new_warehouse.warehouseName,
            'warehouseLocation': new_warehouse.warehouseLocation,
            'business_id': business.id
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getWarehouses(request):
    user = request.user  # Get the authenticated user
    business_id = request.query_params.get('business_id')  # Get the business ID from query parameters

    # Check if business_id is provided
    if not business_id:
        return Response({"error": "business_id query parameter is required"}, status=400)

    # Ensure the business belongs to the authenticated user
    try:
        business = Business.objects.get(id=business_id, owner=user)
    except Business.DoesNotExist:
        return Response({"error": "Business not found or not owned by the user"}, status=404)

    # Fetch warehouses associated with the business
    warehouses = Warehouse.objects.filter(business=business)
    serializer = WarehouseSerializer(warehouses, many=True)
    return Response(serializer.data)




@api_view(['PUT'])
def updateWarehouse(request, pk):
    warehouse = Warehouse.objects.get(id=pk)
    serializer = WarehouseSerializer(instance=warehouse, data=request.data)
    if serializer.is_valid():
        serializer.save()
    return Response(serializer.data)

@api_view(['DELETE'])
def deleteWarehouse(request, pk):
    warehouse = Warehouse.objects.get(id=pk)
    warehouse.delete()
    return Response("Warehouse was deleted")

class PurchaseViewSet(viewsets.ModelViewSet):
    queryset = Purchase.objects.all()
    serializer_class = PurchaseSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        customer = get_object_or_404(Customer, id=self.request.data.get('customer_id'))
        transaction = get_object_or_404(Transaction, id=self.request.data.get('transaction_id'))
        product = get_object_or_404(Product, id=self.request.data.get('product_id'))
        serializer.save(customer=customer, transaction=transaction, product=product)

@api_view(['GET'])
def list_purchases(request):
    purchases = Purchase.objects.all()
    serializer = PurchaseSerializer(purchases, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_customer_purchases(request, customer_id):
    purchases = Purchase.objects.filter(customer__id=customer_id)
    serializer = PurchaseSerializer(purchases, many=True)
    return Response(serializer.data)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_purchase(request, pk):
    purchase = get_object_or_404(Purchase, pk=pk)
    serializer = PurchaseSerializer(purchase, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def create_purchase(request):
    if request.method == 'POST':
        customer_id = request.POST['customer_id']
        product_id = request.POST['product_id']
        transaction_id = request.POST['transaction_id']
        quantity = int(request.POST['quantity'])
        business_id = request.POST['business_id']

        customer = get_object_or_404(Customer, id=customer_id)
        product = get_object_or_404(Product, id=product_id)
        transaction = get_object_or_404(Transaction, id=transaction_id)
        business = get_object_or_404(Business, id=business_id)

        if product.quantity < quantity:
            return JsonResponse({'error': 'Not enough quantity in stock'}, status=400)

        purchase = Purchase(
            customer=customer,
            product=product,
            transaction=transaction,
            quantity=quantity,
            business=business
        )
        purchase.save()

        # Reduce product quantity
        product.reduce_quantity(quantity)

        return JsonResponse({'message': 'Purchase created successfully', 'purchase_id': purchase.id})

def add_installment(request):
    if request.method == 'POST':
        purchase_id = request.POST['purchase_id']
        amount_paid = float(request.POST['amount_paid'])
        next_payment_date = request.POST.get('next_payment_date')

        purchase = get_object_or_404(Purchase, id=purchase_id)

        remaining_balance = purchase.total_amount - amount_paid
        installment = Installment(
            purchase=purchase,
            payment_date=date.today(),
            amount_paid=amount_paid,
            remaining_balance=remaining_balance,
            next_payment_date=next_payment_date
        )
        installment.save()

        return JsonResponse({'message': 'Installment added successfully', 'installment_id': installment.id})


def generate_reference():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))


def send_sms_after_sale(customer, sale, business):
    try:
        # Check if the sale has items and gather product details
        items = sale.items.all()
        if not items:
            logger.error(f"No products found in sale ID {sale.id}")
            return

        # Format product details into a list-like structure
        product_details = "\n".join([
            f"- {item.quantity} x {item.product.product_name}" for item in items
        ])
        logger.info(f"Products found: {product_details}")

        # Retrieve other sale and business details safely
        customer_name = f"**{customer.name}**" if customer else "Mteja"
        business_name = f"**{business.businessName}**" if business else "Biashara isiyojulikana"
        business_phone = business.businessPhoneNumber if business else "N/A"
        total_amount = sale.total_amount

        # Compose the message with bold-like formatting
        message_body = (
            f"Asante {customer_name} kwa kununua bidhaa zifuatazo kutoka {business_name}:\n"
            f"{product_details}\n"
            f"Jumla ya gharama: {total_amount} TSh.\n"
            f"Karibu tena kwa mahitaji yako, na kwa mawasiliano zaidi piga {business_phone}.\n"
            f"Tunathamini wateja wetu!"
        )

        # Send SMS
        send_sms(customer.phoneNumber, message_body)

    except Product.DoesNotExist:
        logger.error(f"Product in sale ID {sale.id} does not exist.")
    except Exception as e:
        logger.error(f"Error processing sale ID {sale.id}: {str(e)}", exc_info=True)



def send_sms(phone_number, message_body):
    """ Function to send SMS using an external SMS service. """
    url = 'https://messaging-service.co.tz/api/sms/v1/text/single'
    headers = {
        'Authorization': "Basic YXRoaW06TWFtYXNob2tv",
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    payload = {
        "from": "OTP",
        "to": phone_number,
        "text": message_body,
        "reference": generate_reference(),  # Ensure you have a function to generate a reference
    }

    try:
        response = requests.post(url, headers=headers, json=payload)

        if response.status_code == 200:
            logger.info("SMS sent successfully to %s", phone_number)
        else:
            logger.error(f"Failed to send SMS: {response.status_code} {response.text}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Error sending SMS to {phone_number}: {str(e)}", exc_info=True)

        
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_sales(request):
    logger.info(f"Received sales data: {request.data}")  # Log the received data

    # Extract the items from the request data
    items_data = request.data.get('items', [])
    if not items_data:
        return Response({'error': 'No items provided for the sale.'}, status=status.HTTP_400_BAD_REQUEST)

    # Extract the transaction_id from the request data
    transaction_id = request.data.get('transaction_id')
    if not transaction_id:
        return Response({'error': 'transaction_id is required.'}, status=status.HTTP_400_BAD_REQUEST)

    # Fetch the Transaction object using the transaction_id
    try:
        transaction = Transaction.objects.get(id=transaction_id)
    except Transaction.DoesNotExist:
        return Response({'error': f"Transaction with ID {transaction_id} does not exist."}, status=status.HTTP_404_NOT_FOUND)

    # Prepare the data for the serializer
    sales_data = request.data.copy()
    sales_data['transaction_id'] = transaction.id  # Use the Transaction instance
    
    # Create the sale object using the provided transaction and business_id
    serializer = SalesSerializer(data=sales_data)
    if serializer.is_valid():
        try:
            # Save the Sale object
            sale = serializer.save(transaction_id=transaction)  # Pass the Transaction instance

            # Initialize total amount for the sale
            total_amount = 0

            # Loop through each item in the items_data
            for item_data in items_data:
                product_id = item_data.get('product_id')
                quantity = item_data.get('quantity')
                price_per_unit = item_data.get('price_per_unit')

                # Fetch the product
                try:
                    product = Product.objects.get(id=product_id)
                except Product.DoesNotExist:
                    logger.error(f"Product with ID {product_id} does not exist.")
                    return Response({'error': f"Product with ID {product_id} does not exist."}, status=status.HTTP_404_NOT_FOUND)

                # Calculate the total price for the SalesItem
                total_price = quantity * price_per_unit

                # Create the SalesItem for the sale
                SalesItem.objects.create(
                    sale=sale,
                    product=product,
                    quantity=quantity,
                    price_per_unit=price_per_unit,
                    total_price=total_price
                )

                # Update the total amount for the Sale
                total_amount += total_price

            # Update the sale total_amount
            sale.total_amount = total_amount
            sale.save()

            logger.info(f"Sales created successfully with ID: {sale.id}")

            # Fetch customer and business details if needed for SMS
            customer_id = request.data.get('customer_id')
            business_id = sale.business.id

            try:
                customer = Customer.objects.get(id=customer_id)
                business = sale.business
            except Customer.DoesNotExist:
                logger.error(f"Customer with ID {customer_id} does not exist.")
                return Response({'error': f"Customer with ID {customer_id} does not exist."}, status=status.HTTP_404_NOT_FOUND)
            except Business.DoesNotExist:
                logger.error(f"Business with ID {business_id} does not exist.")
                return Response({'error': f"Business with ID {business_id} does not exist."}, status=status.HTTP_404_NOT_FOUND)

            # Send SMS after sale is created (assume you have this function)
            send_sms_after_sale(customer, sale, business)

            return Response({'message': 'Sales created successfully', 'sales_id': sale.id}, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error(f"Error saving sales: {str(e)}", exc_info=True)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        logger.error(f"Sales validation errors: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SyncSaleView(APIView):
    def post(self, request):
        try:
            transaction_id = request.data.get('transaction_id')

            # Check if the transaction already exists
            transaction, created = Transaction.objects.get_or_create(
                id=transaction_id,
                defaults={
                    'transaction_type': request.data.get('transaction_type'),
                    'transaction_date': request.data.get('transaction_date'),
                    'business_id': request.data.get('business_id'),
                    'customer_id': request.data.get('customer'),
                    'total_amount': request.data.get('total_amount'),
                    'outstanding_amount': request.data.get('outstanding_amount'),
                    'is_synced': request.data.get('is_synced', False),
                    'is_deleted': request.data.get('is_deleted', False),
                }
            )

            if not created:
                # If the transaction exists, you can log it or update fields as needed
                print(f"Transaction {transaction_id} already exists. Skipping creation.")

            return Response(
                {'message': 'Transaction synced successfully' if created else 'Transaction already exists'},
                status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_purchase(request, pk):
    try:
        purchase = Purchase.objects.get(pk=pk)
    except Purchase.DoesNotExist:
        return Response({'error': 'Purchase not found'}, status=status.HTTP_404_NOT_FOUND)

    purchase.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_expense(request):
    # Print the incoming data to the console
    print("Received data:", request.data)
    
    # Continue with the normal processing of data
    serializer = ExpenseSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_expenses(request):
    # Get the business_id from the query parameters
    business_id = request.query_params.get('business_id')

    # Check if the business_id exists in the query parameters
    if business_id is None:
        return Response({"error": "business_id query parameter is required"}, status=400)

    try:
        # Fetch the Business object based on the business_id
        business = Business.objects.get(id=business_id)
    except Business.DoesNotExist:
        return Response({"error": "Business not found"}, status=404)

    # Filter expenses by the business
    expenses = Expense.objects.filter(business=business)
    serializer = ExpenseSerializer(expenses, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_expense(request, pk):
    try:
        expense = Expense.objects.get(pk=pk, business=request.user.business)
    except Expense.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    serializer = ExpenseSerializer(expense)
    return Response(serializer.data)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_expense(request, pk):
    try:
        expense = Expense.objects.get(pk=pk, business=request.user.business)
    except Expense.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    serializer = ExpenseSerializer(expense, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_expense(request, pk):
    try:
        expense = Expense.objects.get(pk=pk, business=request.user.business)
    except Expense.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    expense.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


#new methods  they have business id and also ensure authentication:

@api_view(['GET'])
def product_suggestions(request):
    query = request.GET.get('q', '')  # Get the query parameter 'q'
    business_id = request.GET.get('business_id', None)  # Optional: filter by business_id

    if not query:
        return Response({'error': 'Query parameter is missing'}, status=400)

    # Query the database for matching products
    products = Product.objects.filter(product_name__icontains=query)

    if business_id:
        products = products.filter(business_id=business_id)

    # Serialize the products
    serializer = ProductSuggestionSerializer(products, many=True)
    
    return Response({'suggestions': serializer.data})


class ExpensePolicyListCreateView(generics.ListCreateAPIView):
    """
    GET: List all expense policies for the authenticated user.
    POST: Create a new expense policy.
    """
    serializer_class = ExpensePolicySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ExpensePolicy.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ExpensePolicyDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET: Retrieve a specific expense policy.
    PUT/PATCH: Update the policy.
    DELETE: Delete the policy.
    """
    serializer_class = ExpensePolicySerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        return ExpensePolicy.objects.filter(user=self.request.user)