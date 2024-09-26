from datetime import date, timedelta, timezone
from decimal import ROUND_HALF_UP, Decimal
from venv import logger
from django.shortcuts import render
from rest_framework.decorators import api_view,permission_classes
from rest_framework.response import Response
from django.http import JsonResponse
from .serializers import ExpenseSerializer, InstallmentSerializer, ProductSerializer, ProductSuggestionSerializer, SalesSerializer,SupplierSerializer,CategorySerializer
from .serializers import TransactionSerializer,WarehouseSerializer,PurchaseSerializer
from .models import Expense, Installment, Product, Sales,Supplier,Category,Transaction,Warehouse,Purchase
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework import status,viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework import filters
from rest_framework.generics  import ListAPIView
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from registration.models import Business, Customer
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
        print("Request Data:", data)

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
            'location_identifier': request.data.get('location_identifier'),  # New field
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

        # Validate supplier
        if product_data['supplier_id']:
            try:
                supplier = Supplier.objects.get(id=product_data['supplier_id'])
            except Supplier.DoesNotExist:
                errors.append('Supplier nottt found')

        # Validate category
        if product_data['category_id']:
            try:
                category = Category.objects.get(id=product_data['category_id'])
            except Category.DoesNotExist:
                errors.append('Category not found')

        # Validate warehouse
        if product_data['warehouse_id']:
            try:
                warehouse = Warehouse.objects.get(id=product_data['warehouse_id'])
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
            error_message = f'Error creating product: {str(e)}'
            logger.error(error_message)
            return Response({'error': error_message}, status=status.HTTP_400_BAD_REQUEST)

        # Return the serialized product data
        serializer = self.get_serializer(new_product)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class SyncProductsView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        """
        Handles syncing products from the client to the server.
        Supports bulk update and creation for better performance.
        """
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

        new_products = []
        updated_products = []
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
                    updated_products.append(product_serializer)  # Append to update list
                else:
                    logger.error(f"Error updating product: {product_serializer.errors}")
                    return Response(product_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                logger.info(f"Creating new product: {product_data.get('product_name')}")
                product_serializer = ProductSerializer(data=product_data)
                if product_serializer.is_valid():
                    new_products.append(product_serializer)  # Append to create list
                else:
                    logger.error(f"Error creating product: {product_serializer.errors}")
                    return Response(product_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Perform bulk create and update operations
        try:
            with transaction.atomic():  # Ensure atomicity of operations
                # Create new products in bulk
                if new_products:
                    Product.objects.bulk_create([serializer.save(commit=False) for serializer in new_products])
                    synced_products.extend([serializer.data for serializer in new_products])

                # Update products in bulk
                if updated_products:
                    Product.objects.bulk_update([serializer.instance for serializer in updated_products],
                                                ['price', 'quantity', 'product_name', 'category'])  # List of fields to update
                    synced_products.extend([serializer.data for serializer in updated_products])

        except Exception as e:
            logger.error(f"Error in bulk operations: {str(e)}")
            return Response({"error": "Failed to sync products"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        logger.info(f"Returning synced products: {synced_products}")
        return Response({
            'synced_products': synced_products,
        }, status=status.HTTP_200_OK)

@api_view(['DELETE'])
def deleteProduct(request,pk):
    product = Product.objects.get(id=pk)
    product.delete()
    return Response("Product was deleted")

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

    serializer = SupplierSerializer(data=supplier_data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    else:
        # Log the errors if the data is not valid
        logger.error(f"Validation errors: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



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
    
    # Log the modified data
    logger.debug(f"Modified transaction data: {data}")

    serializer = TransactionSerializer(data=data)
    if serializer.is_valid():
        try:
            transaction = serializer.save()  # Save the transaction
            logger.info(f"Transaction saved successfully: {serializer.data}")

            # Handle installments automatically if the transaction type is 'loan'
            if transaction.transaction_type == 'loan':
                # Generate installments based on the transaction details
                installments_data = generateInstallmentsForTransaction(transaction)

                for installment_data in installments_data:
                    # Include the transaction ID in each installment's data
                    installment_data['transaction'] = transaction.id
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
        logger.error(f"Validation errors: {serializer.errors}")
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
            'due_date': (transaction.transaction_date + timedelta(days=30*(i+1))).isoformat(),
            'business_id': transaction.business.id,
        }
        installments_data.append(installment_data)

    return installments_data


@api_view(['POST'])
def create_installment(request):
    serializer = InstallmentSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
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



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_sales(request):
    logger.info(f"Received sales data: {request.data}")  # Log the received data
    serializer = SalesSerializer(data=request.data)
    if serializer.is_valid():
        try:
            sale = serializer.save()
            logger.info(f"Sales created successfully with ID: {sale.id}")
            return Response({'message': 'Sales created successfully', 'sales_id': sale.id}, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"Error saving sales: {e}", exc_info=True)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    logger.error(f"Sales validation errors: {serializer.errors}")
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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