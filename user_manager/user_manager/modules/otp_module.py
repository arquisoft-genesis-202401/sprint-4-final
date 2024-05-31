import os
from twilio.rest import Client
from ..settings import VARS

class OTPModule:
    def __init__(self):
        """
        Initialize the OTPModule with Twilio client credentials.
        """
        self.account_sid = VARS["ACCOUNT_SID"]
        self.auth_token = VARS["AUTH_TOKEN"]
        self.service_sid = VARS["SERVICE_SID"]
        self.client = Client(self.account_sid, self.auth_token)

    def send_otp(self, phone_number):
        """
        Send an OTP to the given phone number.

        :param phone_number: String, phone number to which the OTP is sent
        :return: None
        """
        verify = self.client.verify.v2.services(self.service_sid)
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