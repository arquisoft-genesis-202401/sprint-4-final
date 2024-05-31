from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.padding import PKCS7
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hmac, hashes
import base64
from ..settings import VARS

class CryptoModule:
    def __init__(self):
        """ Initialize the module with AES key, HMAC key, and IV from environment variables """
        try:
            self.aes_key = base64.urlsafe_b64decode(VARS["AES_KEY"])
            self.hmac_key = base64.urlsafe_b64decode(VARS["HMAC_KEY"])
            self.iv = base64.urlsafe_b64decode(VARS["IV"])
        except TypeError as e:
            raise ValueError("Environment variables for keys and IV are not properly set.") from e

    def encrypt_data(self, data):
        """ Encrypt data using AES CBC mode with PKCS7 padding """
        backend = default_backend()
        cipher = Cipher(algorithms.AES(self.aes_key), modes.CBC(self.iv), backend=backend)
        encryptor = cipher.encryptor()
        padder = PKCS7(algorithms.AES.block_size).padder()
        padded_data = padder.update(data) + padder.finalize()
        encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
        return base64.urlsafe_b64encode(encrypted_data).decode('utf-8')

    def decrypt_data(self, encrypted_data):
        """ Decrypt data using AES CBC mode with PKCS7 padding """
        encrypted_data = base64.urlsafe_b64decode(encrypted_data)
        backend = default_backend()
        cipher = Cipher(algorithms.AES(self.aes_key), modes.CBC(self.iv), backend=backend)
        decryptor = cipher.decryptor()
        padded_data = decryptor.update(encrypted_data) + decryptor.finalize()
        unpadder = PKCS7(algorithms.AES.block_size).unpadder()
        data = unpadder.update(padded_data) + unpadder.finalize()
        return data.decode('utf-8')

    def calculate_hmac(self, data):
        """ Calculate HMAC for the provided data """
        h = hmac.HMAC(self.hmac_key, hashes.SHA256(), backend=default_backend())
        h.update(data)
        return base64.urlsafe_b64encode(h.finalize()).decode('utf-8')