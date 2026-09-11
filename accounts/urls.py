from django.urls import path

from . import views

app_name = "accounts"


urlpatterns = [
    path("otp/request/", views.otp_request_view, name="otp_request"),
    path("otp/verify/", views.otp_verify_view, name="otp_verify"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("wallet/", views.wallet_detail, name="wallet_detail"),
    path("wallet/charge/", views.wallet_charge, name="wallet_charge"),
    path("wallet/transactions/", views.wallet_transactions, name="wallet_transactions"),
]
