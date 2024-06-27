# views.py
from rest_framework import viewsets,generics,status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import CustomUser, Business,Customer
from rest_framework.decorators import api_view, permission_classes
from rest_framework_simplejwt.tokens import RefreshToken
import logging
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .serializers import  BusinessSerializer,UserRegistrationSerializer,UserLoginSerializer,CustomerSerializer

logger = logging.getLogger(__name__)

class RegisterUserView(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserRegistrationSerializer

    def create(self, request, *args, **kwargs):
        try:
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
        data = request.data
        # Check if user exists and retrieve it
        try:
            user = CustomUser.objects.get(phone_number=data.get('phone_number'))
        except CustomUser.DoesNotExist:
            logger.warning(f"User with phone number {data.get('phone_number')} does not exist.")
            return Response({'status': 'error', 'message': 'User does not exist.'}, status=status.HTTP_400_BAD_REQUEST)

        data['owner'] = user.id  # Assuming owner field expects user id

        try:
            with transaction.atomic():
                serializer = self.get_serializer(data=data)
                serializer.is_valid(raise_exception=True)
                business = serializer.save()
                logger.info(f"Business registered successfully: {business}")
                return Response({
                    'status': 'success',
                    'business_id': business.id,
                    'business': BusinessSerializer(business).data
                }, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"Error registering business: {str(e)}", exc_info=True)
            return Response({'status': 'error', 'message': 'Failed to register business.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LoginView(generics.GenericAPIView):
    serializer_class = UserLoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_200_OK)

class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        business_id = self.request.query_params.get('business_id')
        if business_id:
            return Customer.objects.filter(business__id=business_id)
        return Customer.objects.all()

    def perform_create(self, serializer):
        business = get_object_or_404(Business, id=self.request.data.get('business_id'))
        serializer.save(business=business)





@api_view(['POST'])
@permission_classes([IsAuthenticated])
def switch_business(request):
    business_id = request.data.get('business_id')
    business = get_object_or_404(Business, unique_id=business_id)
    return Response({'business_type': business.type}, status=status.HTTP_200_OK)

@api_view(['GET'])
def list_users(request):
    users = CustomUser.objects.all()
    serializer = UserRegistrationSerializer(users, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_customers(request):
    business_id = request.query_params.get('business_id')
    if business_id:
        customers = Customer.objects.filter(business__id=business_id)
    else:
        customers = Customer.objects.all()
    serializer = CustomerSerializer(customers, many=True)
    return Response(serializer.data)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_customer(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    serializer = CustomerSerializer(customer, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



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
            'body': {'phone_number': '', 'password': '', 'role': ''},
            'description': 'Create a new user'
        },
        {
            'Endpoint': '/users/<int:id>/',
            'method': 'PUT',
            'body': {'phone_number': '', 'password': '', 'role': ''},
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


