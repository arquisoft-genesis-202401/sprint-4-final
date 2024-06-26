from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_http_methods
import requests
from .services.user_service import create_customer_application_service
from .services.user_service import update_application_basic_info_service
from .services.user_service import get_basic_information_by_application_service
from .services.user_service import get_latest_application_service
from .services.user_service import bind_phone_service
import traceback
import sys
import json
from .settings import VARS

@require_http_methods(['POST'])
def send_otp_to_phone(request):
    try:
        # Assuming JSON data is sent in the request; validate as needed
        data = json.loads(request.body.decode('utf-8'))
        
        # Payload Checks
        if len(data) != 1:
            return HttpResponseBadRequest("Invalid payload fields")
        if 'phone_number' not in data:
            return HttpResponseBadRequest("Missing required field: phone_number")
        
        # Extract phone number from request
        phone_number = data['phone_number']
        
        # Call the service function to send an OTP
        auth_service = AuthService()
        status = auth_service.send_otp(phone_number)
        
        if status == "pending":
            return JsonResponse({'message': 'OTP sent successfully.', 'phone_number': phone_number})
        else:
            return HttpResponseBadRequest(f"Failed to send OTP")
    
    except Exception as e:
        traceback.print_exc(file=sys.stdout)
        return HttpResponseBadRequest(f"An error occurred: {str(e)}")
    
@require_http_methods(['POST'])
def create_customer_application(request):
    try:
        # Assuming JSON data is sent in request; validate as needed
        data = json.loads(request.body.decode('utf-8'))

        # Expanded Payload Checks

        required_keys = ["document_type", "document_number", "otp", "phone_number"]
        if len(data) != len(required_keys):
            return HttpResponseBadRequest("Invalid payload fields")
        if not all(key in data for key in required_keys):
            return HttpResponseBadRequest("Missing required fields")

        # Extract data from request
        document_type = data['document_type']
        document_number = data['document_number']
        otp = data['otp']
        phone_number = data['phone_number']

        # Verify OTP
        #auth_service = AuthService()
        #if not auth_service.verify_otp(phone_number, otp):
            #return HttpResponseBadRequest("Invalid OTP")

        # Call the service function to create customer application
        application_id = create_customer_application_service(
            document_type, document_number
        )

        result = bind_phone_service(document_type, document_number, application_id, phone_number)

        # Handle service function responses
        error_messages = ["Customer not found.", "Application not found.", "Access denied. Updates can only be made to the most recent application."]
        if result in error_messages:
            return HttpResponseBadRequest(result)

        # Generate token
        auth_service = AuthService()
        token = auth_service.create_token(application_id)

        # Return the application ID and token
        return JsonResponse({
            'application_id': application_id,
            'token': token
        })

    except Exception as e:
        traceback.print_exc(file=sys.stdout)
        message = str(e)
        if "twilio" in message.lower():
            message = "Non existing OTP verification"
        return HttpResponseBadRequest(f"An error occurred: {message}")

@require_http_methods(['POST'])
def get_customer_latest_application(request):
    try:
        # Assuming JSON data is sent in request; validate as needed
        data = json.loads(request.body.decode('utf-8'))

        # Payload Checks
        required_keys = ["document_type", "document_number", "otp", "phone_number"]
        if len(data) != len(required_keys):
            return HttpResponseBadRequest("Invalid payload fields")
        if not all(key in data for key in required_keys):
            return HttpResponseBadRequest("Missing or invalid required fields")

        # Extract data from request
        document_type = data['document_type']
        document_number = data['document_number']
        otp = data['otp']
        phone_number = data['phone_number']

        # Verify OTP
        auth_service = AuthService()
        if not auth_service.verify_otp(phone_number, otp):
            return HttpResponseBadRequest("Invalid OTP")

        # Call the service function to get the latest application
        result = get_latest_application_service(document_type, document_number, phone_number)
        if "error" in result:
            return HttpResponseBadRequest(result["error"])
        application_id = result["application_id"]

        # Generate token
        auth_service = AuthService()
        token = auth_service.create_token(application_id)

        # Return the application ID and token
        return JsonResponse({
            'application_id': application_id,
            'token': token
        })

    except Exception as e:
        traceback.print_exc(file=sys.stdout)
        message = str(e)
        if "twilio" in message.lower():
            message = "Non existing OTP verification"
        return HttpResponseBadRequest(f"An error occurred: {str(e)}")
    
@require_http_methods(['POST'])
def update_application_basic_info(request, application_id):
    try:
        # Extract the token from the request headers
        token = request.headers.get('Authorization')
        if not token:
            return HttpResponseBadRequest("Authorization token is missing.")

        # Initialize AuthService and verify the token
        auth_service = AuthService()
        if not auth_service.verify_token(token):
            return HttpResponseBadRequest("Invalid or expired token.")

        # Extract the application ID from the token
        token_application_id = auth_service.get_application_id(token)
        if token_application_id != application_id:
            return HttpResponseBadRequest("Token application ID does not match the requested application ID.")

        # Assuming JSON data is sent in request; validate as needed
        data = json.loads(request.body.decode('utf-8'))
        
        # Payload Checks
        required_keys = ["document_type", "document_number", "first_name", "last_name", "country", "state", "city", "address", "email"]
        if len(data) != len(required_keys):
            return HttpResponseBadRequest("Invalid payload fields")
        if not all(key in data for key in required_keys):
            return HttpResponseBadRequest("Missing or invalid required fields")

        # Extract data from request
        document_type = data['document_type']
        document_number = data['document_number']
        first_name = data['first_name']
        last_name = data['last_name']
        country = data['country']
        state = data['state']
        city = data['city']
        address = data['address']
        email = data['email']

        # Call the service function
        result = update_application_basic_info_service(
            document_type, document_number, application_id, first_name, last_name, country, state, city, address, email
        )

        # Handle service function responses
        error_messages = ["Customer not found.", "Application not found.", "Access denied. Updates can only be made to the most recent application.", "BasicInformation not found for the provided Application ID"]
        if result in error_messages:
            return HttpResponseBadRequest(result)

        # If all goes well, return the application ID
        return JsonResponse({'application_id': result})

    except Exception as e:
        traceback.print_exc(file=sys.stdout)
        return HttpResponseBadRequest(f"An error occurred: {str(e)}")

@require_http_methods(['GET'])
def get_basic_information(request, application_id):
    try:
        # Extract the token from the request headers
        token = request.headers.get('Authorization')
        if not token:
            return HttpResponseBadRequest("Authorization token is missing.")

        # Initialize AuthService and verify the token
        auth_service = AuthService()
        if not auth_service.verify_token(token):
            return HttpResponseBadRequest("Invalid or expired token.")

        # Extract the application ID from the token
        token_application_id = auth_service.get_application_id(token)
        if token_application_id != application_id:
            return HttpResponseBadRequest("Token application ID does not match the requested application ID.")

        # Assuming JSON data is sent in request; validate as needed
        data = json.loads(request.body.decode('utf-8'))

        # Payload Checks
        required_keys = ["document_type", "document_number"]
        if len(data) != len(required_keys):
            return HttpResponseBadRequest("Invalid payload fields")
        if not all(key in data for key in required_keys):
            return HttpResponseBadRequest("Missing or invalid required fields")

        # Extract data from request
        document_type = data['document_type']
        document_number = data['document_number']

        # Call the service function with verified application ID
        result = get_basic_information_by_application_service(document_type, document_number, application_id)

        # Handle possible errors
        if 'error' in result:
            return HttpResponseBadRequest(result['error'])

        # Return the decrypted information as JSON
        return JsonResponse(result)

    except Exception as e:
        traceback.print_exc(file=sys.stdout)
        return HttpResponseBadRequest(f"An error occurred: {str(e)}")
    


class AuthService:
    def __init__(self):
        self.auth_manager_ip = VARS["PRIVATE_IP_AUTH_MANAGER"]
        self.create_token_url = f"http://{self.auth_manager_ip}:8080/create_token/"
        self.verify_token_url = f"http://{self.auth_manager_ip}:8080/verify_token/"
        self.get_application_id_url = f"http://{self.auth_manager_ip}:8080/get_application_id/"
        self.send_otp_url = f"http://{self.auth_manager_ip}:8080/send_otp/"
        self.verify_otp_url = f"http://{self.auth_manager_ip}:8080/verify_otp/"

    def create_token(self, application_id):
        if isinstance(application_id, bytes):
            application_id = application_id.decode('utf-8')
        payload = {'application_id': application_id}
        headers = {'Content-Type': 'application/json'}
        response = requests.post(self.create_token_url, data=json.dumps(payload), headers=headers)
        response.raise_for_status()
        return response.json().get('token')

    def verify_token(self, token):
        if isinstance(token, bytes):
            token = token.decode('utf-8')
        payload = {'token': token}
        headers = {'Content-Type': 'application/json'}
        response = requests.post(self.verify_token_url, data=json.dumps(payload), headers=headers)
        response.raise_for_status()
        result = str(response.json().get('is_valid')).lower()
        if result == "true":
            True
        return False

    def get_application_id(self, token):
        if isinstance(token, bytes):
            token = token.decode('utf-8')
        payload = {'token': token}
        headers = {'Content-Type': 'application/json'}
        response = requests.post(self.get_application_id_url, data=json.dumps(payload), headers=headers)
        response.raise_for_status()
        return response.json().get('application_id')

    def send_otp(self, phone_number):
        if isinstance(phone_number, bytes):
            phone_number = phone_number.decode('utf-8')
        payload = {'phone_number': phone_number}
        headers = {'Content-Type': 'application/json'}
        response = requests.post(self.send_otp_url, data=json.dumps(payload), headers=headers)
        response.raise_for_status()
        return response.json().get('status')

    def verify_otp(self, phone_number, otp_code):
        if isinstance(phone_number, bytes):
            phone_number = str(phone_number).strip()
        if isinstance(otp_code, bytes):
           otp_code = str(otp_code).strip()
        payload = {'phone_number': phone_number, 'otp_code': otp_code}
        headers = {'Content-Type': 'application/json'}
        response = requests.post(self.verify_otp_url, data=json.dumps(payload), headers=headers)
        response.raise_for_status()
        result = str(response.json().get('is_approved')).lower()
        if result == "true":
            return True
        return False