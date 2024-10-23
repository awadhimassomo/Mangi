import logging
from rest_framework import serializers

from inventory.models import BusinessType
from .models import CustomUser, Business, Customer, Partner
from django.contrib.auth import get_user_model, authenticate
from django.utils.translation import gettext_lazy as _

# Set up logging

logger = logging.getLogger(__name__)

User = get_user_model()

class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'phoneNumber', 'email', 'username', 'role', 'password']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        # Log the validated data
        logger.info(f"Validated Data for User Creation or Fetch: {validated_data}")

        # Try to fetch an existing user based on phone number or username
        user = CustomUser.objects.filter(
            phoneNumber=validated_data.get('phoneNumber')
        ).first()

        if not user:
            # If no user is found, create a new one
            user = CustomUser.objects.create_user(
                phoneNumber=validated_data['phoneNumber'],
                email=validated_data.get('email'),
                username=validated_data.get('username'),
                role=validated_data.get('role'),
                password=validated_data['password']
            )
            logger.info(f"New User Created: {user}")
        else:
            logger.info(f"Existing User Found: {user}")

        # Proceed to register the new business here
        # For example, you might have a separate Business model
        # You can add code here to register the business using the existing or new user

        return user

    # Removed validation methods for phoneNumber and username since they are not unique





class BusinessSerializer(serializers.ModelSerializer):
    owner = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all(), write_only=True)
    businessType = serializers.CharField(write_only=True)  # Accept a name for the business type

    class Meta:
        model = Business
        fields = [
            'id', 'uuid', 'businessName', 'businessAddress', 'businessPhoneNumber',
            'lipaNumber', 'businessType', 'phoneNetwork', 'website', 'qrImage', 
            'hasBenefitedFromOffer', 'owner'
        ]
        read_only_fields = ['id', 'uuid', 'qrImage']

    def create(self, validated_data):
        # Extract the owner from the validated data
        owner = validated_data.pop('owner')

        # Extract the business type name from the validated data
        business_type_name = validated_data.pop('businessType')

        # Retrieve or create the BusinessType instance based on the name
        business_type, created = BusinessType.objects.get_or_create(name=business_type_name)

        # Log whether the BusinessType was created or already existed
        if created:
            logger.info(f"BusinessType '{business_type_name}' created successfully.")
        else:
            logger.info(f"BusinessType '{business_type_name}' already exists.")

        # Assign the BusinessType instance to the validated data
        validated_data['businessType'] = business_type

        # Create the business with the associated owner and businessType
        business = Business.objects.create(owner=owner, **validated_data)
        logger.info(f"Business '{business.businessName}' created for owner ID {owner.id}.")
        return business

    def validate(self, data):
        # Custom validation logic, if needed
        owner = data.get('owner')
        businessName = data.get('businessName')

        if Business.objects.filter(owner=owner, businessName=businessName).exists():
            logger.warning(f"Business name '{businessName}' already exists for owner ID {owner.id}.")
            raise serializers.ValidationError("This business name already exists for the owner.")

        return data


class UserLoginSerializer(serializers.Serializer):
    phoneNumber = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})

    def validate(self, attrs):
        phoneNumber = attrs.get('phoneNumber')
        password = attrs.get('password')

        if phoneNumber and password:
            # Here we're using phoneNumber explicitly
            user = authenticate(phoneNumber=phoneNumber, password=password)
            if user:
                if not user.is_active:
                    msg = _('User account is disabled.')
                    logger.warning(msg)
                    raise serializers.ValidationError(msg, code='authorization')
            else:
                msg = _('Unable to log in with provided credentials.')
                logger.warning(msg)
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = _('Must include "phoneNumber" and "password".')
            logger.warning(msg)
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs
    
class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['id', 'name', 'phoneNumber', 'business', 'date_added']
        read_only_fields = ['id', 'date_added']


class BusinessListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Business
        fields = '__all__'

class PartnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Partner
        fields = '__all__'  # You can also specify fields explicitly if needed
