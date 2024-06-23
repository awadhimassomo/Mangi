# views.py
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import CustomUser, Business
from .serializers import CustomUserSerializer, BusinessSerializer

class RegisterUserView(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer

    @action(detail=False, methods=['post'])
    def register(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({'status': 'success', 'user_id': user.id})
# views.py continued...

class RegisterBusinessView(viewsets.ModelViewSet):
    queryset = Business.objects.all()
    serializer_class = BusinessSerializer

    @action(detail=False, methods=['post'])
    def register(self, request):
        data = request.data
        # Check if user exists and retrieve it
        try:
            user = CustomUser.objects.get(phone_number=data['phone_number'])
        except CustomUser.DoesNotExist:
            return Response({'status': 'error', 'message': 'User does not exist.'}, status=status.HTTP_400_BAD_REQUEST)

        # Proceed to register the business with the retrieved user as the owner
        data['owner'] = user.id  # Assuming owner field expects user id
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        business = serializer.save()
        return Response({'status': 'success', 'business_id': business.id})
