from django.urls import path
from . import views
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    path('create_token/', csrf_exempt(views.create_token), name='create_token'),
    path('verify_token/', csrf_exempt(views.verify_token), name='verify_token'),
    path('get_application_id/', csrf_exempt(views.get_application_id), name='get_application_id'),
    path('send_otp/', csrf_exempt(views.send_otp), name='send_otp'),
    path('verify_otp/', csrf_exempt(views.verify_otp), name='verify_otp'),
]
