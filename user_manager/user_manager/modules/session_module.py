import json
import base64
from datetime import datetime, timezone, timedelta
from .crypto_module import CryptoModule

class SessionModule:
    def __init__(self):
        timezone_offset = -5.0  # UTC-5
        self.tzinfo = timezone(timedelta(hours=timezone_offset))
        self.ttl = timedelta(minutes=15)

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
        cryptoModule = CryptoModule()
        signature = cryptoModule.calculate_hmac((f"{header_json};{payload_json}").encode())
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
            cryptoModule = CryptoModule()
            expected_signature = cryptoModule.calculate_hmac(header_payload.encode())
            if signature != expected_signature:
                return False

            # Verify token expiration
            creation_date = datetime.fromisoformat(header['Creation Date'])
            ttl_minutes = int(header['TTL'])  # TTL is stored as minutes
            ttl = timedelta(minutes=ttl_minutes)
            expiration_date = creation_date + ttl
            
            if datetime.now(self.tzinfo) > expiration_date:
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
