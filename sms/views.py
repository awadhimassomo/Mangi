import json
import random
import string
import uuid
from django.forms import ValidationError
from django.views import View
import requests
from django.utils import timezone
from datetime import datetime, timedelta
from rest_framework import status,viewsets
from django.views.decorators.csrf import csrf_exempt
from sms.otp_service import OTPVerificationService
from .models import NetworkCredit, OTPCredit,BenefitedPhoneNumber
from rest_framework.response import Response
from rest_framework.views import APIView
from .forms import CreditForm
from django.shortcuts import render, redirect
from registration.models import BusinessProfile, CustomUser, Business, Customer, Partner 
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from registration.serializers import BusinessListSerializer, BusinessSerializer, User
import logging
from django.conf import settings
from django.http import JsonResponse
from django.utils.encoding import force_bytes
from  registration.models import CustomUser
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import NetworkCreditSerializer, OTPCreditSerializer,OTPVerifySerializer,ResendOTPSerializer,PasswordResetConfirmSerializer

logger = logging.getLogger(__name__)

class SendOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        personal_number = request.data.get('personal_number')
        business_id = request.data.get('business_id')

        try:
            user = CustomUser.objects.get(phoneNumber=personal_number)
            business = Business.objects.get(id=business_id, owner=user)

            otp_credit, created = OTPCredit.objects.get_or_create(user=user, business=business)

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
        except Business.DoesNotExist:
            return Response({"error": "Business not found or not associated with this user"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def generate_otp():
    return str(random.randint(10000, 99999)).zfill(5)

def generate_reference():
    return str(uuid.uuid4())


class ResendOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        logger.info("Received OTP resend request")
        logger.debug(f"Request data: {request.data}")

        serializer = ResendOTPSerializer(data=request.data)
        if serializer.is_valid():
            phoneNumber = serializer.validated_data['phoneNumber']
            logger.debug(f"Validated phone number: {phoneNumber}")

            try:
                user = CustomUser.objects.get(phoneNumber=phoneNumber)
                logger.debug(f"User found: {user}")

                try:
                    otp_credit = OTPCredit.objects.get(user=user)
                    logger.debug(f"OTP record found: {otp_credit}")

                    # Check if the resend request is too soon
                    if otp_credit.otp_timestamp and (timezone.now() - otp_credit.otp_timestamp).seconds < 60:
                        logger.warning("OTP resend requested too soon")
                        return Response({"error": "OTP resend is allowed after 60 seconds"}, status=status.HTTP_400_BAD_REQUEST)

                    # Generate a new OTP and update the expiry time
                    otp = generate_otp()
                    otp_credit.otp = otp
                    otp_credit.otp_expiry = timezone.now() + timedelta(minutes=10)  # Reset expiry time
                    otp_credit.otp_timestamp = timezone.now()
                    otp_credit.save()
                    logger.info(f"OTP updated and saved: {otp}")

                    # Send OTP via SMS
                    if send_otp_via_sms(phoneNumber, otp):
                        logger.info("OTP sent successfully via SMS")
                        return Response({"message": "OTP resent successfully"}, status=status.HTTP_200_OK)
                    else:
                        logger.error("Failed to send OTP via SMS")
                        return Response({"error": "Failed to resend OTP"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

                except OTPCredit.DoesNotExist:
                    logger.error("No OTP record found for this user")
                    return Response({"error": "No OTP record found for this user"}, status=status.HTTP_404_NOT_FOUND)

            except CustomUser.DoesNotExist:
                logger.error("Personal number not found")
                return Response({"error": "Personal number not found"}, status=status.HTTP_404_NOT_FOUND)
        
        logger.error(f"Serializer validation errors: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

def send_otp_via_sms(phoneNumber, otp):
    try:
        from_ = "OTP"  # Sender name
        url = 'https://messaging-service.co.tz/api/sms/v1/text/single'
        headers = {
            'Authorization': "Basic YXRoaW06TWFtYXNob2tv",
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        reference = generate_reference()  # Generate the reference
        payload = {
            "from": from_,
            "to": phoneNumber,
            "text": f"Your OTP is {otp}",
            "reference": reference,
        }

        # Print the phone number and reference before making the request
        print(f"Sending OTP to: {phoneNumber}, Reference: {reference}")

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


def generate_reference():
    """Generate a unique reference for SMS tracking."""
    return f"REF-{datetime.now().strftime('%Y%m%d%H%M%S')}"




@csrf_exempt  # Bypass CSRF for this endpoint
def daily_report_view(request):
    """Receive the daily report data and trigger SMS to the owner and partners."""
    if request.method == 'POST':
        try:
            # Parse the incoming JSON data
            data = json.loads(request.body)

            # Extract relevant data
            date = data.get('date')
            total_sales = data.get('total_sales', 0.0)
            total_expenses = data.get('total_expenses', 0.0)
            net_amount = data.get('net_amount', 0.0)
            loan_collections = data.get('loan_collections', 0.0)
            phone_number = data.get('phone_number')  # Ensure phone number is provided

            # Validate the phone number
            if not phone_number:
                return JsonResponse({'status': 'error', 'message': 'Phone number is required'}, status=400)

            # Send SMS to the business owner
            send_sms(phone_number, total_sales, total_expenses, net_amount, loan_collections)
            
            # Check for partners and calculate their share
            partners = Partner.objects.all()
            if partners.exists():
                for partner in partners:
                    percentage = partner.percentage  # Get the partner's profit share percentage
                    profit_share = (net_amount * percentage) / 100  # Calculate their share

                    # Construct and send the SMS to the partner
                    partner_message = (
                        f"Dear {partner.name},\n"
                        f"Today's report: Net Profit: {net_amount:.2f}.\n"
                        f"Your share ({percentage}%): {profit_share:.2f}.\n"
                    )
                    send_sms(partner.phone_number, partner_message)

            return JsonResponse({'status': 'success', 'message': 'Report received and SMS sent'}, status=200)

        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON data'}, status=400)

    return JsonResponse({'status': 'error', 'message': 'Only POST requests are allowed'}, status=405)


def send_sms(phone_number, *args):
    """Simulate sending an SMS."""
    if isinstance(args[0], str):
        message = args[0]  # If sending a custom message
    else:
        total_sales, total_expenses, net_amount, loan_collections = args
        message = (
            f"Daily Report:\n"
            f"Total Sales: {total_sales}\n"
            f"Total Expenses: {total_expenses}\n"
            f"Net Profit: {net_amount}\n"
            f"Loan Collections: {loan_collections}"
        )
    print(f"Sending SMS to {phone_number}:")
    print(message)
    
    
def send_sms(phone_number, total_sales, total_expenses, net_amount, loan_collections):
    """Send SMS with the daily business report."""
    message_body = f"""
   REPOTI YA LEO:

    Date: {datetime.now().strftime('%Y-%m-%d')}

    Jumla ya Mauzo: {total_sales:,.2f} Tsh
    Jumla ya Matumizi: {total_expenses:,.2f} Tsh
    Jumla Kuu: {net_amount:,.2f} Tsh
    Madeni yaliokusanywa: {loan_collections:,.2f} Tsh

    Asante na Usiku Mwema.
    """

    url = 'https://messaging-service.co.tz/api/sms/v1/text/single'
    headers = {
        'Authorization': "Basic YXRoaW06TWFtYXNob2tv",  # Replace with valid credentials
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    payload = {
        "from": "OTP",
        "to": phone_number,
        "text": message_body.strip(),  # Remove leading/trailing spaces
        "reference": generate_reference(),
    }

    try:
        response = requests.post(url, headers=headers, json=payload)

        if response.status_code == 200:
            logger.info(f"SMS sent successfully to {phone_number}")
        else:
            logger.error(f"Failed to send SMS: {response.status_code} {response.text}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Error sending SMS to {phone_number}: {str(e)}", exc_info=True)



class SendCreditView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        print(f"Request data received: {request.data}")  # Debugging line

        # Retrieve the correct key from the request data
        business_number = request.data.get('business_phoneNumber')  # Use the correct key
        print(f"Received request to send credit to business number: {business_number}")

        # Check if the phone number has already benefited from the offer
        if BenefitedPhoneNumber.objects.filter(phoneNumber=business_number).exists():
            print(f"Business {business_number} has already benefited from the offer.")
            return Response({"error": "This business has already benefited from the offer"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Retrieve the business by its phone number
            business = Business.objects.get(businessPhoneNumber=business_number)
            print(f"Business found: {business}")

            # Get the network type for the business
            network_type = business.phoneNetwork
            print(f"Searching for OTP credit with network type: {network_type}")

            # Find all unused NetworkCredits with the same network type using case-insensitive matching
            network_credits = NetworkCredit.objects.filter(
                network_type__iexact=network_type,
                used=False
            )


            # Print all NetworkCredits to see if any exist regardless of the network type
            all_credits = NetworkCredit.objects.all()
            print("All network credits in the database:")
            for credit in all_credits:
                print(f"- Credit: {credit.credit}, Network Type: {credit.get_network_type_display()}, Used: {credit.used}")

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
                    business.hasBenefitedFromOffer = True
                    business.save()

                    # Record that this phone number has benefited from the offer
                    BenefitedPhoneNumber.objects.create(phoneNumber=business_number)

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
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            return Response({"error": "An internal error occurred"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def send_credit_via_sms(business_number, credit_value, network_type):
    try:
        from_ = "OTP"  # Sender name
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
    
    
    
#Sms:
def add_credit_view(request):
    if request.method == 'POST':
        form = CreditForm(request.POST)
        if form.is_valid():
            form.save()  # Save the credit to the database
            return JsonResponse({'success': True, 'message': 'Credit successfully added!'})
        else:
            logger.error(f"Form errors: {form.errors}")  # Log form errors
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)
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
    def post(self, request):
        phoneNumber = request.data.get('phoneNumber')
        otp = request.data.get('otp')
        business_id = request.data.get('business_id')

        logger.info(f"Received OTP verification request for phone number: {phoneNumber}, OTP: {otp}, business ID: {business_id}")

        # Step 1: Authenticate the user by verifying the OTP
        try:
            user = CustomUser.objects.get(phoneNumber=phoneNumber)
        except CustomUser.DoesNotExist:
            logger.error(f"User with phone number {phoneNumber} does not exist.")
            raise ValidationError("Invalid phone number or OTP.")

        try:
            otp_record = OTPCredit.objects.get(user=user, otp=otp)
            if timezone.now() > otp_record.otp_expiry:
                raise ValidationError("OTP has expired.")
        except OTPCredit.DoesNotExist:
            logger.error("Invalid OTP provided.")
            raise ValidationError("Invalid phone number or OTP.")

        # Step 2: Mark the user as verified
        if not user.isVerified:
            user.isVerified = True
            user.save()
            logger.info(f"User with phone number {phoneNumber} has been verified successfully.")

        # Step 3: Generate tokens (access and refresh)
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        logger.info(f"Generated tokens for user ID {user.id}: Access token: {access_token}, Refresh token: {refresh_token}")

        # Step 4: Retrieve the user's businesses
        businesses = Business.objects.filter(owner=user)

        if not businesses.exists():
            logger.warning(f"No businesses found for user ID {user.id}.")
            return Response({
                'access_token': access_token,
                'refresh_token': refresh_token,
                'message': 'No businesses associated with this user.'
            }, status=status.HTTP_200_OK)
        else:
            serializer = BusinessSerializer(businesses, many=True)
            logger.info(f"Returning {len(businesses)} businesses for user ID {user.id}.")
            return Response({
                'access_token': access_token,
                'refresh_token': refresh_token,
                'businesses': serializer.data
            }, status=status.HTTP_200_OK)

#password reset
class PasswordResetRequestView(APIView):
    def post(self, request):
        phoneNumber = request.data.get('phoneNumber')  # Using request.data for better compatibility with DRF
        if not phoneNumber:
            return JsonResponse({'error': 'Phone number is required'}, status=400)
        
        if not CustomUser.objects.filter(phoneNumber=phoneNumber).exists():
            return JsonResponse({'error': 'Invalid phone number'}, status=400)
        
        user = CustomUser.objects.get(phoneNumber=phoneNumber)
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        reset_link = request.build_absolute_uri(
            f'/password-reset-confirm/{uid}/{token}/'
        )
        # Generate the message to be sent
        message = f'Click the link to reset your password: {reset_link}'
        if reset_password(user.phoneNumber, message):
            return JsonResponse({'message': 'Password reset link sent successfully'})
        else:
            return JsonResponse({'error': 'Failed to send SMS'}, status=500)

def reset_password(phoneNumber, message):
    try:
        from_ = "OTP"  # Sender name
        url = settings.MESSAGING_SERVICE_URL
        headers = {
            'Authorization': settings.MESSAGING_SERVICE_AUTHORIZATION,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        payload = {
            "from": from_,
            "to": phoneNumber,
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
    
