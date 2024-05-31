import json
import base64
from datetime import datetime, timezone, timedelta

import requests
from twilio.rest import Client
from .settings import VARS

class Auth:
    def __init__(self):
        timezone_offset = -5.0  # UTC-5
        self.tzinfo = timezone(timedelta(hours=timezone_offset))
        self.ttl = timedelta(minutes=15)

        # Initialize Twilio client credentials for OTPModule
        self.account_sid = VARS["ACCOUNT_SID"]
        self.auth_token = VARS["AUTH_TOKEN"]
        self.service_sid = VARS["SERVICE_SID"]
        self.client = Client(self.account_sid, self.auth_token)

    # SessionModule methods
    def serialize_data(self, application_id):
        """ Serialize header and payload into JSON """
        header = {
            "Creation Date": datetime.now(self.tzinfo).isoformat(),
            "TTL": int(self.ttl.total_seconds() / 60)  # Store TTL in minutes as an integer
        }
        payload = {
            "Application ID": application_id
        }
        header_json = json.dumps(header, sort_keys=True)
        payload_json = json.dumps(payload, sort_keys=True)
        return header_json, payload_json

    def encode_token(self, application_id):
        """ Encode the header, payload and signature into a Base64 string """
        header_json, payload_json = self.serialize_data(application_id)
        cryptoService = CryptoService()
        signature = cryptoService.calculate_hmac((f"{header_json};{payload_json}").encode())
        token = f"{header_json};{payload_json};{signature}"
        encoded_token = base64.urlsafe_b64encode(token.encode()).decode()
        return encoded_token

    def create_token(self, application_id):
        """ Generate a complete token with a given application_id """
        return self.encode_token(application_id)

    def verify_token(self, token):
        """ Verify the token by checking the signature and expiration date """
        try:
            decoded_token = base64.standard_b64decode(token).decode("utf-8")
            header_json, payload_json, signature = decoded_token.split(";")
            header = json.loads(header_json)
            header_payload = f"{header_json};{payload_json}"
            
            # Verify signature
            cryptoService = CryptoService()
            expected_signature = cryptoService.calculate_hmac(header_payload.encode())
            if (signature != expected_signature):
                return False

            # Verify token expiration
            creation_date = datetime.fromisoformat(header['Creation Date'])
            ttl_minutes = int(header['TTL'])  # TTL is stored as minutes
            ttl = timedelta(minutes=ttl_minutes)
            expiration_date = creation_date + ttl
            
            if (datetime.now(self.tzinfo) > expiration_date):
                return False  # Token has expired

            return True
        except Exception as e:
            print(f"Error verifying token: {e}")
            return False
    
    def get_application_id(self, token):
        """ Verify the token by checking the signature """
        try:
            decoded_token = base64.standard_b64decode(token).decode("utf-8")
            _, payload_json, _ = decoded_token.split(";")
            payload = json.loads(payload_json)
            application_id = payload["Application ID"]
            return application_id
        except Exception as e:
            print(f"Error obtaining the application id: {e}")
            return "Error"

    # OTPModule methods
    def send_otp(self, phone_number):
        """
        Send an OTP to the given phone number.

        :param phone_number: String, phone number to which the OTP is sent
        :return: None
        """
        verify = self.client.verify.v2.services(self.service_sid)
        print(phone_number)
        print(self.service_sid)
        result = verify.verifications.create(to=phone_number, channel='sms')
        return result.status

    def verify_otp(self, phone_number, otp_code):
        """
        Verify if the entered OTP code is correct for the given phone number.

        :param phone_number: String, phone number to verify OTP against
        :param otp_code: String, the OTP code to verify
        :return: Boolean, True if the OTP is correct, False otherwise
        """
        verify = self.client.verify.v2.services(self.service_sid)
        result = verify.verification_checks.create(to=phone_number, code=str(otp_code))
        return result.status == 'approved'

class CryptoService:
    def __init__(self):
        self.crypto_manager_ip = VARS["PRIVATE_IP_CRYPTO_MANAGER"]
        self.encrypt_url = f"http://{self.crypto_manager_ip}/encrypt"
        self.decrypt_url = f"http://{self.crypto_manager_ip}/decrypt"
        self.hmac_url = f"http://{self.crypto_manager_ip}/hmac"

    def encrypt_data(self, data):
        payload = {'data': data}
        headers = {'Content-Type': 'application/json'}
        response = requests.post(self.encrypt_url, data=json.dumps(payload), headers=headers)
        if response.status_code == 200:
            return response.json().get('message')
        else:
            response.raise_for_status()

    def decrypt_data(self, encrypted_data):
        payload = {'encrypted_data': encrypted_data}
        headers = {'Content-Type': 'application/json'}
        response = requests.post(self.decrypt_url, data=json.dumps(payload), headers=headers)
        if response.status_code == 200:
            return response.json().get('message')
        else:
            response.raise_for_status()

    def calculate_hmac(self, data):
        payload = {'data': data}
        headers = {'Content-Type': 'application/json'}
        response = requests.post(self.hmac_url, data=json.dumps(payload), headers=headers)
        if response.status_code == 200:
            return response.json().get('message')
        else:
            response.raise_for_status()