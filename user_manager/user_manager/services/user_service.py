from django.db import transaction
from ..models import Customer, Application, ApplicationStatus, BasicInformation
from django.utils import timezone
from ..modules.crypto_module import CryptoModule

@transaction.atomic
def create_customer_application_service(document_type, document_number):
    # Check if the customer already exists
    customer, created = Customer.objects.get_or_create(
        DocumentType=document_type,
        DocumentNumber=document_number,
        defaults={'DocumentType': document_type, 'DocumentNumber': document_number}
    )

    # Get the predefined ApplicationStatus for "BasicInfo"
    status, status_created = ApplicationStatus.objects.get_or_create(
        StatusDescription='BasicInfo',
        defaults={'StatusDescription': 'BasicInfo', 'CreationDate': timezone.now(), 'ModificationDate': timezone.now()}
    )

    # Create an Application for this customer with the "BasicInfo" status
    application = Application.objects.create(
        CustomerID=customer,
        StatusID=status,
        CreationDate=timezone.now(),
        ModificationDate=timezone.now()
    )

    return application.id

@transaction.atomic
def get_latest_application_service(document_type, document_number, phone_number):
    try:
        # Fetch the customer based on document type and document number
        customer = Customer.objects.filter(
            DocumentType=document_type,
            DocumentNumber=document_number
        ).first()

        if not customer:
            return {"error": "Customer not found"}  # No customer found with the given details

        # Get the latest application for this customer
        latest_application = Application.objects.filter(
            CustomerID=customer
        ).order_by('-CreationDate').first()  # Order by creation date descending and get the first

        if not latest_application:
            return {"error": "No application found for this customer"}  # No application found for this customer

        # Retrieve the BasicInformation associated with the latest application
        basic_info = BasicInformation.objects.get(ApplicationID=latest_application)
        
        crypto = CryptoModule()

        # Decrypt and verify the phone number
        encrypted_data_hmac = basic_info.MobileNumber
        encrypted_data, stored_hmac = encrypted_data_hmac.split(';')

        # Decrypt the data
        decrypted_data = crypto.decrypt_data(encrypted_data)

        # Calculate HMAC of the decrypted data and compare with stored HMAC
        calculated_hmac = crypto.calculate_hmac(decrypted_data.encode())
        if calculated_hmac != stored_hmac:
            return {"error": "Integrity check failed for phone number"}

        # Compare the decrypted phone number with the provided phone number
        if decrypted_data != phone_number:
            return {"error": "Phone number does not match"}

        # If all checks pass, return the latest application ID
        return {"application_id": latest_application.id}

    except BasicInformation.DoesNotExist:
        return {"error": "BasicInformation not found for the latest application"}
    except Exception as e:
        print(f"Failed to retrieve latest application: {e}")
        return {"error": "An error occurred while retrieving the latest application"}

@transaction.atomic
def bind_phone_service(document_type, document_number, application_id, phone_number):
    try:
        # Fetch the customer based on document type and document number
        customer = Customer.objects.get(DocumentType=document_type, DocumentNumber=document_number)
    except Customer.DoesNotExist:
        return "Customer not found."
    
    try:
        # Fetch the application to be updated
        application = Application.objects.get(pk=application_id, CustomerID=customer)
    except Application.DoesNotExist:
        return "Application not found."

    # Fetch the latest application for the customer
    latest_application = Application.objects.filter(CustomerID=customer).latest('CreationDate')
    
    # Check if the application is the most recent one
    if application.id != latest_application.id:
        return "Access denied. Updates can only be made to the most recent application."

    # Initialize the cryptography module
    crypto = CryptoModule()

    # Encrypt the mobile number with HMAC
    data_to_encrypt = phone_number.encode('utf-8')
    encrypted_data = crypto.encrypt_data(data_to_encrypt)
    data_hmac = crypto.calculate_hmac(data_to_encrypt)
    encrypted_phone_number = encrypted_data + ";" + data_hmac

    # Create the BasicInformation linked to the application with empty fields except for the encrypted mobile number
    BasicInformation.objects.create(
        ApplicationID=application,
        FirstName='',
        LastName='',
        Country='',
        State='',
        City='',
        Address='',
        MobileNumber=encrypted_phone_number,
        Email='',
        CreationDate=timezone.now(),
        ModificationDate=timezone.now()
    )

    return application_id

@transaction.atomic
def update_application_basic_info_service(document_type, document_number, application_id, first_name, last_name, country, state, city, address, email):
    # Fetch the customer based on document type and document number
    try:
        customer = Customer.objects.get(DocumentType=document_type, DocumentNumber=document_number)
    except Customer.DoesNotExist:
        return "Customer not found."
    
    # Fetch the application to be updated
    try:
        application = Application.objects.get(pk=application_id, CustomerID=customer)
    except Application.DoesNotExist:
        return "Application not found."

    # Fetch the latest application for the customer
    latest_application = Application.objects.filter(CustomerID=customer).latest('CreationDate')
    
    # Check if the application is the most recent one
    if application.id != latest_application.id:
        return "Access denied. Updates can only be made to the most recent application."

    # Initialize the cryptography module
    crypto = CryptoModule()

    # Encrypt and store each field individually with HMAC
    fields = [first_name, last_name, country, state, city, address, email]
    field_names = ['FirstName', 'LastName', 'Country', 'State', 'City', 'Address', 'Email']
    encrypted_data_dict = {}

    for index, field in enumerate(fields):
        data_to_encrypt = field.encode('utf-8')
        encrypted_data = crypto.encrypt_data(data_to_encrypt)
        data_hmac = crypto.calculate_hmac(data_to_encrypt)
        encrypted_field = encrypted_data + ";" + data_hmac
        encrypted_data_dict[field_names[index]] = encrypted_field

    try:
        # Fetch the BasicInformation linked to the application
        basic_information = BasicInformation.objects.get(ApplicationID=application)
    except BasicInformation.DoesNotExist:
        return "BasicInformation not found for the provided Application ID"

    # Update the data in the BasicInformation
    for key, value in encrypted_data_dict.items():
        setattr(basic_information, key, value)
    basic_information.ModificationDate = timezone.now()
    basic_information.save()

    return application_id

def get_basic_information_by_application_service(document_type, document_number, application_id):
    try:
        # Fetch the customer based on document type and document number
        customer = Customer.objects.get(DocumentType=document_type, DocumentNumber=document_number)
    except Customer.DoesNotExist:
        return {"error": "Customer not found."}
    
    try:
        # Fetch the application to be verified
        application = Application.objects.get(pk=application_id, CustomerID=customer)
    except Application.DoesNotExist:
        return {"error": "Application not found."}

    try:
        # Ensure the application is the most recent one for the customer
        latest_application = Application.objects.filter(CustomerID=customer).latest('CreationDate')
        if latest_application.id != application_id:
            return {"error": "Access denied. Only the most recent application's basic information can be retrieved."}

        # Retrieve the BasicInformation associated with the given Application ID
        basic_info = BasicInformation.objects.get(ApplicationID__id=application_id)
        crypto = CryptoModule()

        # Decrypt and verify each encrypted field
        fields = ['FirstName', 'LastName', 'Country', 'State', 'City', 'Address', 'MobileNumber', 'Email']
        decrypted_info = {}
        
        for field in fields:
            encrypted_data_hmac = getattr(basic_info, field)
            encrypted_data, stored_hmac = encrypted_data_hmac.split(';')

            # Decrypt the data
            decrypted_data = crypto.decrypt_data(encrypted_data)

            # Calculate HMAC of the decrypted data and compare with stored HMAC
            calculated_hmac = crypto.calculate_hmac(decrypted_data.encode())
            if calculated_hmac != stored_hmac:
                return {"error": f"Integrity check failed for {field}"}

            decrypted_info[field.lower()] = decrypted_data

        return decrypted_info

    except BasicInformation.DoesNotExist:
        # Return an error dictionary if no BasicInformation is found for the given Application ID
        return {"error": "BasicInformation not found for the provided Application ID"}