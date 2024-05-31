from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from .views import  send_otp_to_phone, create_customer_application, update_application_basic_info, get_basic_information, get_customer_latest_application

urlpatterns = [
    path('create-application/', csrf_exempt(create_customer_application), name='create_application'),
    path('update-application/<int:application_id>/', csrf_exempt(update_application_basic_info), name='update_application'),
    path('get-basic-information/<int:application_id>/', csrf_exempt(get_basic_information), name='get_basic_information'),
    path('send-otp/', csrf_exempt(send_otp_to_phone), name='send-otp'),
    path('latest-application/', csrf_exempt(get_customer_latest_application), name='get_customer_latest_application'),
]
