from django.urls import path
from .views import request_otp, verify_otp , register , user_login, user_logout, profile, wallet, deposit, withdraw, transaction_history

urlpatterns = [
    path('otp/request/', request_otp, name='request_otp'),
    path('otp/verify/', verify_otp, name='verify_otp'),

    path('register/', register, name='register'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),

    path('profile/', profile, name='profile'),

    path('wallet/', wallet, name='wallet'),
    path('wallet/deposit/', deposit, name='deposit'),
    path('wallet/withdraw/', withdraw, name='withdraw'),
    path("wallet/transactions/", transaction_history, name="transaction_history"),
]

app_name = 'accounts'
