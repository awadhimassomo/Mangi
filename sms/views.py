import random
import uuid
import requests
from django.utils import timezone
from rest_framework import status,viewsets
from .models import NetworkCredit, OTPCredit,BenefitedPhoneNumber
from rest_framework.response import Response
from rest_framework.views import APIView
from .forms import CreditForm
from django.shortcuts import render, redirect
from registration.models import CustomUser, Business 
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from .serializers import NetworkCreditSerializer, OTPCreditSerializer,OTPVerifySerializer,ResendOTPSerializer

class SendOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        personal_number = request.data.get('personal_number')
        try:
            user = CustomUser.objects.get(phone_number=personal_number)
            otp_credit, created = OTPCredit.objects.get_or_create(user=user)

            otp = generate_otp()
            otp_credit.otp = otp
            otp_credit.otp_timestamp = timezone.now()
            otp_credit.save()

            if send_otp_via_sms(personal_number, otp):
                return Response({"message": "OTP sent successfully"}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Failed to send OTP"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except CustomUser.DoesNotExist:
            return Response({"error": "Personal number not found"}, status=status.HTTP_404_NOT_FOUND)


def generate_otp():
    return str(random.randint(10000, 99999)).zfill(5)

def generate_reference():
    return str(uuid.uuid4())


class ResendOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        print(f"Request data: {request.data}")  # Print the entire request data

        serializer = ResendOTPSerializer(data=request.data)
        if serializer.is_valid():
            phone_number = serializer.validated_data['phone_number']
            print(f"Received phone number: {phone_number}")

            try:
                user = CustomUser.objects.get(phone_number=phone_number)
                print(f"User found: {user}")

                try:
                    otp_credit = OTPCredit.objects.get(user=user)
                    print(f"OTP record found: {otp_credit}")

                    if otp_credit.otp_timestamp and (timezone.now() - otp_credit.otp_timestamp).seconds < 60:
                        return Response({"error": "OTP resend is allowed after 60 seconds"}, status=status.HTTP_400_BAD_REQUEST)

                    otp = generate_otp()
                    otp_credit.otp = otp
                    otp_credit.otp_timestamp = timezone.now()
                    otp_credit.save()
                    print(f"OTP updated and saved: {otp}")

                    if send_otp_via_sms(phone_number, otp):
                        print("OTP sent successfully via SMS")
                        return Response({"message": "OTP resent successfully"}, status=status.HTTP_200_OK)
                    else:
                        return Response({"error": "Failed to resend OTP"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

                except OTPCredit.DoesNotExist:
                    print("No OTP record found for this user")
                    return Response({"error": "No OTP record found for this user"}, status=status.HTTP_404_NOT_FOUND)

            except CustomUser.DoesNotExist:
                print("Personal number not found")
                return Response({"error": "Personal number not found"}, status=status.HTTP_404_NOT_FOUND)
        
        print(f"Serializer errors: {serializer.errors}")  # Print serializer errors if any
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

def send_otp_via_sms(phone_number, otp):
    try:
        from_ = "RMNDR"  # Sender name
        url = 'https://messaging-service.co.tz/api/sms/v1/text/single'
        headers = {
            'Authorization': "Basic YXRoaW06TWFtYXNob2tv",
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        reference = generate_reference()  # Generate the reference
        payload = {
            "from": from_,
            "to": phone_number,
            "text": f"Your OTP is {otp}",
            "reference": reference,
        }

        # Print the phone number and reference before making the request
        print(f"Sending OTP to: {phone_number}, Reference: {reference}")

        response = requests.post(url, headers=headers, json=payload)

        if response.status_code == 200:
            print("OTP message sent successfully!")
            return True
        else:
            print("Failed to send OTP message.")
            print(response.status_code)
            print(response.text)
            return False
    except Exception as e:
        print(f'Error sending OTP: {e}')
        return False



class SendCreditView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        business_number = request.data.get('business_phone_number')
        print(f"Received request to send credit to business number: {business_number}")


         # Check if the phone number has already benefited from the offer
        if BenefitedPhoneNumber.objects.filter(phone_number=business_number).exists():
            print(f"Business {business_number} has already benefited from the offer.")
            return Response({"error": "This business has already benefited from the offer"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Retrieve the business by its phone number
            business = Business.objects.get(business_phone_number=business_number)
            print(f"Business found: {business}")

          

            # Get the network type for the business
            network_type = business.phone_network
            print(f"Searching for OTP credit with network type: {network_type}")

            # Find all unused NetworkCredits with the same network type
            network_credits = NetworkCredit.objects.filter(
                network_type=network_type,
                used=False
            )

            if network_credits.exists():
                print(f"Network credits found for network type {network_type}:")
                for credit in network_credits:
                    print(f"- Credit: {credit.credit}, Network Type: {credit.get_network_type_display()}")

                # For simplicity, let's assume we send the first available credit
                first_credit = network_credits.first()

                # Mark the credit as used
                first_credit.used = True
                first_credit.save()

        

                if send_credit_via_sms(business_number, first_credit.credit, first_credit.get_network_type_display()):
                    print(f"Credit value {first_credit.credit} sent successfully to {business_number}")

                    # Update the business to show it has benefited from the offer
                    business.has_benefited_from_offer = True
                    business.save()

                        # Record that this phone number has benefited from the offer
                    BenefitedPhoneNumber.objects.create(phone_number=business_number)

                    return Response({"message": "Credit value sent successfully"}, status=status.HTTP_200_OK)
                else:
                    # If sending fails, revert the used status of the credit
                    first_credit.used = False
                    first_credit.save()
                    print(f"Failed to send credit value {first_credit.credit} to {business_number}")
                    return Response({"error": "Failed to send credit value"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                print(f"No available network credits for network type: {network_type}")
                return Response({"error": "No available network credits for this network type"}, status=status.HTTP_404_NOT_FOUND)
        
        except Business.DoesNotExist:
            print(f"Business number not found: {business_number}")
            return Response({"error": "Business number not found"}, status=status.HTTP_404_NOT_FOUND)



def send_credit_via_sms(business_number, credit_value, network_type):
    try:
        from_ = "RMNDR"  # Sender name
        url = 'https://messaging-service.co.tz/api/sms/v1/text/single'
        headers = {
            'Authorization': "Basic YXRoaW06TWFtYXNob2tv",
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        payload = {
            "from": from_,
            "to": business_number,
            "text": f"Asante kwa jiunga Kujiunga na APP yetu ya Mangi umepokea vocha ya {network_type} \n {credit_value} .",
            "reference": generate_reference(),
        }
        response = requests.post(url, headers=headers, json=payload)

        if response.status_code == 200:
            print("Credit message sent successfully!")
            return True
        else:
            print("Failed to send credit message.")
            print(response.status_code)
            print(response.text)
            return False
    except Exception as e:
        print(f'Error sending credit: {e}')
        return False


def add_credit_view(request):
    if request.method == 'POST':
        form = CreditForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('credit_success')
    else:
        form = CreditForm()
    return render(request, 'add_credit.html', {'form': form})

def credit_success_view(request):
    return render(request, 'credit_success.html')

class NetworkCreditViewSet(viewsets.ModelViewSet):
    queryset = NetworkCredit.objects.all()
    serializer_class = NetworkCreditSerializer

class OTPCreditViewSet(viewsets.ModelViewSet):
    queryset = OTPCredit.objects.all()
    serializer_class = OTPCreditSerializer

class VerifyOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = OTPVerifySerializer(data=request.data)
        if serializer.is_valid():
            mobile_number = serializer.validated_data.get('mobile_number')
            otp = serializer.validated_data.get('otp')

            try:
                # Retrieve the OTP record
                otp_record = OTP.objects.get(mobile_number=mobile_number, otp=otp)

                # Check if the OTP has expired
                if (timezone.now() - otp_record.created_at).total_seconds() > 300:  # OTP expires after 5 minutes
                    return Response({"error": "OTP has expired"}, status=status.HTTP_400_BAD_REQUEST)

                # OTP is valid
                user, created = CustomUser.objects.get_or_create(phone_number=mobile_number)
                businesses = Business.objects.filter(user=user)
                business_serializer = BusinessListSerializer(businesses, many=True)
                refresh = RefreshToken.for_user(user)
                access_token = refresh.access_token

                return Response({
                    "message": "OTP verified successfully",
                    "refresh": str(refresh),
                    "access": str(access_token),
                    "businesses": business_serializer.data
                }, status=status.HTTP_200_OK)

            except OTP.DoesNotExist:
                return Response({"error": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST)

        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#password reset:

class PasswordResetRequestView(APIView):
    def post(self, request):
        phone_number = request.POST.get('phone_number')
        try:
            user = UserModel.objects.get(phone_number=phone_number)
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            reset_link = request.build_absolute_uri(
                f'/password-reset-confirm/{uid}/{token}/'
            )
            # Generate the message to be sent
            message = f'Click the link to reset your password: {reset_link}'
            if reset_password(user.phone_number, message):
                return JsonResponse({'message': 'Password reset link sent successfully'})
            else:
                return JsonResponse({'error': 'Failed to send SMS'}, status=500)
        except UserModel.DoesNotExist:
            return JsonResponse({'error': 'Invalid phone number'}, status=400)


def reset_password(phone_number, message):
    try:
        from_ = "RMNDR"  # Sender name
        url = settings.MESSAGING_SERVICE_URL
        headers = {
            'Authorization': settings.MESSAGING_SERVICE_AUTHORIZATION,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        payload = {
            "from": from_,
            "to": phone_number,
            "text": message,  # The message parameter is used here
            "reference": generate_reference(),
        }
        response = requests.post(url, headers=headers, json=payload)

        if response.status_code == 200:
            print("SMS sent successfully!")
            return True
        else:
            print("Failed to send SMS.")
            print(response.status_code)
            print(response.text)
            return False
    except Exception as e:
        print(f'Error sending SMS: {e}')
        return False


#comfirming password

class PasswordResetConfirmView(APIView):
    def post(self, request, uidb64, token):
        serializer = PasswordResetConfirmSerializer(data={
            'uid': uidb64,
            'token': token,
            'new_password': request.data.get('new_password')
        })
        
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Password reset successfully'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)