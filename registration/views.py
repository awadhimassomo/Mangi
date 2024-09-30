# views.py
import logging
from django.apps import apps
from django.views import View
from rest_framework import viewsets,generics,status
from rest_framework.response import Response
from rest_framework.decorators import action

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
            logger.warning(" not provided in the request data.")
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
        
        
@api_view(['POST'])
def login_view(request):
    phoneNumber = request.data.get('phoneNumber')
    password = request.data.get('password')
    
    user = authenticate(request, username=phoneNumber, password=password)
    
    if user is not None:
        refresh = RefreshToken.for_user(user)
        
        # Debugging output
        print(f"User: {user.username}")  
        print(f"Refresh Token: {str(refresh)}")  
        print(f"Access Token: {str(refresh.access_token)}")  
        
        # Retrieve businesses associated with the user
        businesses = Business.objects.filter(owner=user)
        print(f"Businesses for user {user.id}: {businesses}")
        
        businesses_data = [
            {
                "id": b.id,
                "businessName": b.businessName,
                "businessAddress": b.businessAddress,
                "businessPhoneNumber": b.businessPhoneNumber,
                "lipaNumber": b.lipaNumber,
                "businessType": b.businessType,
                "phoneNetwork": b.phoneNetwork,
            }
            for b in businesses
        ]
        
        # Extract additional user details
        email = user.email
        role = user.role.name if user.role else None  # Assuming user.role is a foreign key to a Role model
        is_staff = user.is_staff
        vcard_qrImage = user.vcard_qrImage.url if user.vcard_qrImage else None

        # Print additional user details for debugging
        print(f"Email: {email}")
        print(f"Role: {role}")
        print(f"Is Staff: {is_staff}")
        print(f"VCard QR Image: {vcard_qrImage}")

        # Include the owner ID (user ID) in the response
        owner_id = user.id
        print(f"Owner ID: {owner_id}")

        # Return the response with the access token and additional user details
        return Response({
            'username': user.username,
            'email': email,
            'phoneNumber': phoneNumber,
            'role': role,
            'is_staff': is_staff,
            'vcard_qrImage': vcard_qrImage,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'owner_id': owner_id,  # Include the owner ID in the response
            'businesses': businesses_data
        })
    else:
        print("Invalid credentials")
        return Response({"error": "Invalid credentials"}, status=400)

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
            business_data = {
                'id': business.id,
                'uuid': business.uuid,
                'businessName': business.businessName,
                'businessAddress': business.businessAddress,
                'businessPhoneNumber': business.businessPhoneNumber,
                'lipaNumber': business.lipaNumber,
                'businessType': business.businessType,
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
            raise Http404("Business not found")


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


