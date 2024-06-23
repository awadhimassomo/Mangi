from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import JsonResponse
from .serializers import ProductSerializer,SupplierSerializer,CategorySerializer,TransactionSerializer,WarehouseSerializer
from .models import Product,Supplier,Category,Transaction,Warehouse
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework import status
from rest_framework import filters
from rest_framework.generics  import ListAPIView
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend




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
            'body':{'supplier_name':""},
            'description':'Create a supplier with data sent via post'
        },

         {
          'Endpoint' : '/Suppliers/id/update/',
            'method':'PUT',
            'body':{'supplier_name':""},
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
            'body':{'WarehouseName':""},
            'description':'Create a warehouse with data sent via post'
        },

         {
          'Endpoint' : '/Warehouses/id/update/',
            'method':'PUT',
            'body':{'WarehouseName':""},
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


@api_view(['GET'])
def getProducts(request):
    products = Product.objects.all()
    serializer = ProductSerializer(products,many=True)
    return Response(serializer.data)

  

@api_view(['GET'])
def  getNote(request,pk):
    product=Product.objects.all()
    serializer=ProductSerializer(product,many=False)
    return Response(serializer.data)

@api_view(['PUT'])
def updateProduct(request,pk):
    data = request.data
    product = Product.objects.get(id=pk)
    serializer = ProductSerializer(instance=product,data=data)
    if serializer.is_valid():
        serializer.save()
    return Response(serializer.data)

# Product viesets

class ProductViewSet(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['ProductName', 'Barcode', 'Price', 'Cost', 'Quantity']




class CreateProduct(generics.CreateAPIView):
    serializer_class = ProductSerializer

    def create(self, request, *args, **kwargs):
        # Extracting fields from request.data
        product_data = {
            'product_name': request.data.get('ProductName'),
            'Barcode': request.data.get('Barcode'),
            'price': request.data.get('Price'),
            'cost': request.data.get('Cost'),
            'quantity': request.data.get('Quantity'),
            'supplier_name': request.data.get('Supplier'),
            'warehouse_name': request.data.get('Warehouse'),
            'Category_id': request.data.get('Category')
        }

        # Mandatory field validations
        mandatory_fields = ['product_name', 'Barcode', 'price', 'cost', 'quantity']
        for field in mandatory_fields:
            if not product_data[field]:
                return Response({'error': f'{field.replace("_", " ").title()} is required'}, 
                                status=status.HTTP_400_BAD_REQUEST)

        # Finding optional related objects
        supplier = None
        if product_data['supplier_name']:
            try:
                supplier = Supplier.objects.get(pk=product_data['supplier_name'])
            except Supplier.DoesNotExist:
                return Response({'error': 'Supplier not found'}, status=status.HTTP_404_NOT_FOUND)
            except ValueError:
                return Response({'error': 'Invalid supplier ID'}, status=status.HTTP_400_BAD_REQUEST)

        category = None
        if product_data['Category_id']:
            try:
                category = Category.objects.get(pk=product_data['Category_id'])
            except Category.DoesNotExist:
                return Response({'error': 'Category does not exist'}, status=status.HTTP_404_NOT_FOUND)

        warehouse = None
        if product_data['warehouse_name']:
            try:
                warehouse = Warehouse.objects.get(pk=product_data['warehouse_name'])
            except Warehouse.DoesNotExist:
                return Response({'error': 'Warehouse does not exist'}, status=status.HTTP_404_NOT_FOUND)

        # Creating the product
        try:
            new_product = Product.objects.create(
                ProductName=product_data['product_name'],
                Price=product_data['price'],
                Cost=product_data['cost'],
                Quantity=product_data['quantity'],
                Supplier=supplier,  # These may be None if not provided
                Warehouse=warehouse,
                Category=category,
                Barcode=product_data['Barcode']
            )
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # Return the serialized product data
        serializer = self.get_serializer(new_product)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        


@api_view(['DELETE'])
def deleteProduct(request,pk):
    product = Product.objects.get(id=pk)
    product.delete()
    return Response("Product was deleted")

# Views for the Supplier model
@api_view(['GET'])
def getSuppliers(request):
    suppliers = Supplier.objects.all()
    serializer = SupplierSerializer(suppliers, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def createSupplier(request):
    serializer = SupplierSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
    return Response(serializer.data)

@api_view(['PUT'])
def updateSupplier(request, pk):
    supplier = Supplier.objects.get(id=pk)
    serializer = SupplierSerializer(instance=supplier, data=request.data)
    if serializer.is_valid():
        serializer.save()
    return Response(serializer.data)

@api_view(['DELETE'])
def deleteSupplier(request, pk):
    supplier = Supplier.objects.get(id=pk)
    supplier.delete()
    return Response("Supplier was deleted")

# Views for the Category model
@api_view(['GET'])
def getCategories(request):
    categories = Category.objects.all()
    serializer = CategorySerializer(categories, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def createCategory(request):
    serializer = CategorySerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
    return Response(serializer.data)

@api_view(['PUT'])
def updateCategory(request, pk):
    category = Category.objects.get(id=pk)
    serializer = CategorySerializer(instance=category, data=request.data)
    if serializer.is_valid():
        serializer.save()
    return Response(serializer.data)

@api_view(['DELETE'])
def deleteCategory(request, pk):
    category = Category.objects.get(id=pk)
    category.delete()
    return Response("Category was deleted")

# Views for the Transaction model
@api_view(['GET'])
def getTransactions(request):
    transactions = Transaction.objects.all()
    serializer = TransactionSerializer(transactions, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def createTransaction(request):
    serializer = TransactionSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
    return Response(serializer.data)

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


class CreateWarehouses(generics.CreateAPIView):
    serializer_class = WarehouseSerializer

    def create(self, request, *args, **kwargs):
        # Extract form data from request.data
        WarehouseName = request.data.get('WarehouseName')
        WarehouseLocation = request.data.get('WarehouseLocation')


        # Create a new Warehouse object
        new_warehouse = Warehouse.objects.create(
            WarehouseName=WarehouseName,
             WarehouseLocation=WarehouseLocation
        )

        # Serialize the new object
        serializer = WarehouseSerializer(new_warehouse)

        return Response(serializer.data, status=status.HTTP_201_CREATED)
        
@api_view(['GET'])
def getWarehouses(request):
    warehouses = Warehouse.objects.all()
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







