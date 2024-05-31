# auth_app/views.py
import json
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .auth_module import Auth

@require_http_methods(["POST"])
def create_token(request):
    data = json.loads(request.body)
    application_id = data.get('application_id')
    if application_id:
        auth_instance = Auth()
        token = auth_instance.create_token(application_id)
        return JsonResponse({'token': token})
    return JsonResponse({'error': 'application_id is required'}, status=400)

@require_http_methods(["POST"])
def verify_token(request):
    data = json.loads(request.body)
    token = data.get('token')
    if token:
        auth_instance = Auth()
        is_valid = auth_instance.verify_token(token)
        return JsonResponse({'is_valid': is_valid})
    return JsonResponse({'error': 'token is required'}, status=400)

@require_http_methods(["POST"])
def get_application_id(request):
    data = json.loads(request.body)
    token = data.get('token')
    if token:
        auth_instance = Auth()
        application_id = auth_instance.get_application_id(token)
        return JsonResponse({'application_id': application_id})
    return JsonResponse({'error': 'token is required'}, status=400)

@require_http_methods(["POST"])
def send_otp(request):
    data = json.loads(request.body)
    phone_number = data.get('phone_number')
    if phone_number:
        auth_instance = Auth()
        status = auth_instance.send_otp(phone_number)
        return JsonResponse({'status': status})
    return JsonResponse({'error': 'phone_number is required'}, status=400)

@require_http_methods(["POST"])
def verify_otp(request):
    data = json.loads(request.body)
    phone_number = data.get('phone_number')
    otp_code = data.get('otp_code')
    if phone_number and otp_code:
        auth_instance = Auth()
        is_approved = auth_instance.verify_otp(phone_number, otp_code)
        return JsonResponse({'is_approved': is_approved})
    return JsonResponse({'error': 'phone_number and otp_code are required'}, status=400)
