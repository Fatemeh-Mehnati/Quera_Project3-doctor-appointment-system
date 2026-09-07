from django.urls import path
from .views import all

urlpatterns = [
    path('otp/request/', request_otp, name='request_otp'),
]

app_name = 'appointments'