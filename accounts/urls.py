from django.urls import path
from .views import request_otp, verify_otp , register , user_login, user_logout, profile

urlpatterns = [
    path('otp/request/', request_otp, name='request_otp'),
    path('otp/verify/', verify_otp, name='verify_otp'),

    path('register/', register, name='register'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),

    path('profile/', profile, name='profile'),
]

app_name = 'accounts'
