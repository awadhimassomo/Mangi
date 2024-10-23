# views.py
import logging
from django.apps import apps
from django.views import View
from rest_framework import viewsets,generics,status
from rest_framework.response import Response
from rest_framework.decorators import action

from inventory.models import BusinessType, PublicProduct
from inventory.serializers import ProductSerializer
from sms.models import NetworkCredit
from .models import CustomUser, Business,Customer, Partner
from rest_framework.decorators import api_view, permission_classes
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.db import transaction
from django.http import Http404, JsonResponse
from django.contrib.auth import get_user_model, authenticate
from .serializers import CustomerSerializer, PartnerSerializer
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .serializers import  BusinessSerializer,UserRegistrationSerializer,UserLoginSerializer,CustomerSerializer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RegisterUserView(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserRegistrationSerializer

    def create(self, request, *args, **kwargs):
        try:
            # Print the received data
            print(f"Received Data: {request.data}")

            # Log the received data
            logger.debug(f"Received Data: {request.data}")

            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                user = serializer.save()
                logger.info(f"User registered successfully: {user}")
                return Response({
                    'status': 'success',
                    'user_id': user.id,
                    'user':  UserRegistrationSerializer(user).data
                }, status=status.HTTP_201_CREATED)
            else:
                logger.error(f"Validation errors: {serializer.errors}")
                return Response({'status': 'error', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error registering user: {str(e)}", exc_info=True)
            return Response({'status': 'error', 'message': 'Failed to register user.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class RegisterBusinessView(viewsets.ModelViewSet):
    queryset = Business.objects.all()
    serializer_class = BusinessSerializer

    @action(detail=False, methods=['post'])
    def register(self, request):
        logger.debug(f"Full Request Data: {request.data}")

        data = request.data

        # Extract the owner ID from the request data
        owner_id = data.get('owner')
        if owner_id is None:
            logger.warning("Owner ID not provided in the request data.")
            return Response({'status': 'error', 'message': 'Owner ID is required.'}, status=status.HTTP_400_BAD_REQUEST)

        logger.debug(f"Searching for User with Owner ID: {owner_id}")

        # Check if user exists and retrieve it
        try:
            user = CustomUser.objects.get(id=owner_id)
            logger.debug(f"Obtained User ID: {user.id}, Phone Number: {user.phoneNumber}")
        except CustomUser.DoesNotExist:
            logger.warning(f"User with ID {owner_id} does not exist.")
            return Response({'status': 'error', 'message': 'User does not exist.'}, status=status.HTTP_400_BAD_REQUEST)

        # Add the user to the owners list
        data['owner'] = user.id

   

        try:
            with transaction.atomic():
                # Log the data that will be passed to the serializer
                logger.debug(f"Data sent to serializer: {data}")

                serializer = self.get_serializer(data=data)
                if not serializer.is_valid():
                    logger.error(f"Validation Errors: {serializer.errors}")
                    return Response({
                        'status': 'error',
                        'errors': serializer.errors,
                        'received_data': data  # Include the received data in the response
                    }, status=status.HTTP_400_BAD_REQUEST)

                business = serializer.save()

                logger.debug(f"Business Saved: {vars(business)}")

                if not business.owner:
                    logger.error("Owner is missing after saving the business.")
                    raise Exception("Owner is missing after saving the business.")

                logger.info(f"Business registered successfully: {business}")

                response_data = {
                    'status': 'success',
                    'id': business.id,
                    'business': BusinessSerializer(business).data
                }
                logger.debug(f"Final Response Data: {response_data}")
                return Response(response_data, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"Error registering business: {str(e)}", exc_info=True)
            return Response({
                'status': 'error',
                'message': f"Failed to register business. Details: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    def _sync_public_products_to_business(self, business):
        # Fetch public products associated with the new business's businessType
        public_products = PublicProduct.objects.filter(business_type=business.businessType)
        
        if not public_products.exists():
            logger.info(f"No public products found for businessType: {business.businessType}")
            return
        
        # Create new products in this business based on public products
        for public_product in public_products:
            product_data = {
                'barcode': public_product.barcode,
                'product_name': public_product.product_name,
                'business': business.id,  # Associate with the new business
                # Add other fields as needed, using public_product's fields
            }

            # Create a new Product for this business
            product_serializer = ProductSerializer(data=product_data)
            if product_serializer.is_valid():
                product_serializer.save()
                logger.info(f"Product {public_product.product_name} added to business {business.name}")
            else:
                logger.error(f"Failed to create product for business {business.name}: {product_serializer.errors}")

        
        
@api_view(['POST'])
def login_view(request):
    phoneNumber = request.data.get('phoneNumber')
    password = request.data.get('password')
    
    user = authenticate(request, username=phoneNumber, password=password)
    
    if user is not None:
        if not user.isVerified:
            # Custom response for unverified accounts
            return Response({
                "error": "Account not verified",
                "message": "Your account is not verified. Please verify your account to proceed."
            }, status=498)
        
        # Generate tokens
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)
        
        # Retrieve businesses associated with the user
        businesses = Business.objects.filter(owner=user)
        businesses_data = [
            {
                "id": b.id,
                "businessName": b.businessName,
                "businessAddress": b.businessAddress,
                "businessPhoneNumber": b.businessPhoneNumber,
                "lipaNumber": b.lipaNumber,
                "businessType": b.businessType.name if b.businessType else None,
                "phoneNetwork": b.phoneNetwork,
            }
            for b in businesses
        ]
        
        # Extract additional user details
        email = user.email
        role = user.role.name if user.role else None  # Assuming user.role is a foreign key to a Role model
        is_staff = user.is_staff
        vcard_qrImage = user.vcard_qrImage.url if user.vcard_qrImage else None

        # Include the owner ID (user ID) in the response
        owner_id = user.id

        # Return the response with the access token and additional user details
        return Response({
            'username': user.username,
            'email': email,
            'phoneNumber': phoneNumber,
            'role': role,
            'is_staff': is_staff,
            'vcard_qrImage': vcard_qrImage,
            'refresh': refresh_token,
            'access': access_token,
            'owner_id': owner_id,
            'businesses': businesses_data
        })
    else:
        # Return an error response for invalid credentials
        return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

#importating data

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def register_customer(request):
    data = request.data
    business_id = data.get('business_id')

    print(f'Received data: {data}')  # Debugging print
    print(f'Received business_id: {business_id}')  # Debugging print

    # Fetch the business object
    business = get_object_or_404(Business, id=business_id)
    print(f'Fetched business: {business}')  # Debugging print

    phoneNumber = data.get('phoneNumber')
    if not phoneNumber:
        return Response({'error': 'Phone number is required'}, status=status.HTTP_400_BAD_REQUEST)

    # Use get_or_create to fetch or create the Customer instance
    customer, created = Customer.objects.get_or_create(
        phoneNumber=phoneNumber,
        business=business,  # Pass the Business instance directly
        defaults=data
    )
    
    if not created:
        # Update fields if necessary, e.g., increment frequency
        customer.frequency += 1
        customer.save()
    
    # Use the CustomerSerializer to serialize the customer object
    serializer = CustomerSerializer(customer)
    
    if created:
        print('Customer created and saved')  # Debugging print
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    else:
        print('Customer already existed, updated frequency')  # Debugging print
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    try:
        refresh_token = request.data.get('refresh')
        if refresh_token is None:
            return Response({"detail": "Refresh token is missing"}, status=400)
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response({"detail": "Logout successful"}, status=200)
    except Exception as e:
        return Response({"detail": str(e)}, status=400)


def get_businessType(request):
    try:
        business = Business.objects.get(owner=request.user)
        return JsonResponse({'businessType': business.businessType}, status=200)
    except Business.DoesNotExist:
        return JsonResponse({'error': 'Business not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def switch_business(request):
    business_id = request.data.get('business_id')
    business = get_object_or_404(Business, unique_id=business_id)
    return Response({'businessType': business.type}, status=status.HTTP_200_OK)

@api_view(['GET'])
def list_users(request):
    users = CustomUser.objects.all()
    serializer = UserRegistrationSerializer(users, many=True)
    return Response(serializer.data)




@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_partners(request):
    business_id = request.query_params.get('business_id')
    if business_id:
        partners = Partner.objects.filter(business_id=business_id)
    else:
        partners = Partner.objects.all()
    serializer = PartnerSerializer(partners, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_partner(request):
    serializer = PartnerSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def retrieve_partner(request, pk):
    partner = get_object_or_404(Partner, pk=pk)
    serializer = PartnerSerializer(partner)
    return Response(serializer.data)

@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_partner(request, pk):
    partner = get_object_or_404(Partner, pk=pk)
    serializer = PartnerSerializer(partner, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_partner(request, pk):
    partner = get_object_or_404(Partner, pk=pk)
    partner.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


class BusinessListView(View):
    def get(self, request):
        businesses = Business.objects.all().values('id', 'businessName', 'businessType', 'businessAddress')
        business_list = list(businesses)  # Convert QuerySet to a list
        return JsonResponse(business_list, safe=False)


class BusinessDetailView(View):
    def get(self, request, id):
        try:
            business = Business.objects.get(pk=id)
            
            # If businessType is a foreign key, you can access its name or ID like this:
            business_type_data = business.businessType.name if business.businessType else None
            
            # Alternatively, if it's a many-to-many relationship:
            # business_type_data = [bt.name for bt in business.businessType.all()]
            
            business_data = {
                'id': business.id,
                'uuid': business.uuid,
                'businessName': business.businessName,
                'businessAddress': business.businessAddress,
                'businessPhoneNumber': business.businessPhoneNumber,
                'lipaNumber': business.lipaNumber,
                'businessType': business_type_data,
                'phoneNetwork': business.phoneNetwork,
                'website': business.website,
                'owner': business.owner.id,  # Include only the owner ID
                'qrImage': business.qrImage.url if business.qrImage else None,  # Serialize as URL
                'isSynced': business.isSynced,
                'lastSyncTime': business.lastSyncTime.isoformat() if business.lastSyncTime else None,
                'isDeleted': business.isDeleted,
                'hasBenefitedFromOffer': business.hasBenefitedFromOffer,
            }
            return JsonResponse(business_data)
        except Business.DoesNotExist:
            return JsonResponse({'error': 'Business not found'}, status=404)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated, IsAdminUser])
def delete_user(request, pk):
    try:
        user = CustomUser.objects.get(id=pk)
        user.delete()
        return Response("User was deleted", status=status.HTTP_200_OK)
    except CustomUser.DoesNotExist:
        return Response("User not found", status=status.HTTP_404_NOT_FOUND)

@api_view(['PUT'])
@permission_classes([IsAuthenticated, IsAdminUser])
def update_user(request, pk):
    try:
        user = CustomUser.objects.get(id=pk)
        serializer = UserRegistrationSerializer(instance=user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except CustomUser.DoesNotExist:
        return Response("User not found", status=status.HTTP_404_NOT_FOUND)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_business(request, pk):
    try:
        business = Business.objects.get(id=pk)
        business.delete()
        return Response("Business was deleted", status=status.HTTP_200_OK)
    except Business.DoesNotExist:
        return Response("Business not found", status=status.HTTP_404_NOT_FOUND)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_business(request, pk):
    try:
        business = Business.objects.get(id=pk)
        serializer = BusinessSerializer(instance=business, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Business.DoesNotExist:
        return Response("Business not found", status=status.HTTP_404_NOT_FOUND)
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])  # Requires token authentication
def sync_customers(request):
    try:
        # Log the incoming request data
        logging.info(f"Received data: {request.data}")
        
        # Get the data from the request body
        customers_data = request.data
        
        # Process each customer from the request
        for customer_data in customers_data:
            Customer.objects.update_or_create(
                id=customer_data.get('id'),
                defaults={
                    'name': customer_data.get('name'),
                    'phoneNumber': customer_data.get('phoneNumber'),
                    'tinNumber': customer_data.get('tinNumber'),
                    'date_added': customer_data.get('date_added'),
                    'business_id': customer_data.get('business_id'),  # Ensure business_id is saved
                    'isDeleted': customer_data.get('isDeleted', False),
                    'isSynced': customer_data.get('isSynced', False),
                    'frequency': customer_data.get('frequency', 0),
                }
            )

        # Return a success response
        return Response({'status': 'success', 'message': 'Customers synced successfully.'})

    except Exception as e:
        logging.error(f"Error while syncing customers: {e}")
        return Response({'status': 'error', 'message': str(e)}, status=400)
    


@api_view(['GET'])
def get_routes(request):
    routes = [
        {
            'Endpoint': '/users/',
            'method': 'GET',
            'body': None,
            'description': 'Return a list of users'
        },
        {
            'Endpoint': '/users/<int:id>/',
            'method': 'GET',
            'body': None,
            'description': 'Return a single user'
        },
        {
            'Endpoint': '/users/',
            'method': 'POST',
            'body': {'phoneNumber': '', 'password': '', 'role': ''},
            'description': 'Create a new user'
        },
        {
            'Endpoint': '/users/<int:id>/',
            'method': 'PUT',
            'body': {'phoneNumber': '', 'password': '', 'role': ''},
            'description': 'Update an existing user'
        },
        {
            'Endpoint': '/users/<int:id>/',
            'method': 'DELETE',
            'body': None,
            'description': 'Delete an existing user'
        },
        {
            'Endpoint': '/businesses/',
            'method': 'GET',
            'body': None,
            'description': 'Return a list of businesses'
        },
        {
            'Endpoint': '/businesses/<int:id>/',
            'method': 'GET',
            'body': None,
            'description': 'Return a single business'
        },
        {
            'Endpoint': '/businesses/',
            'method': 'POST',
            'body': {'name': '', 'type': '', 'unique_id': ''},
            'description': 'Create a new business'
        },
        {
            'Endpoint': '/businesses/<int:id>/',
            'method': 'PUT',
            'body': {'name': '', 'type': '', 'unique_id': ''},
            'description': 'Update an existing business'
        },
        {
            'Endpoint': '/businesses/<int:id>/',
            'method': 'DELETE',
            'body': None,
            'description': 'Delete an existing business'
        }

        
    ]
    return Response(routes)


