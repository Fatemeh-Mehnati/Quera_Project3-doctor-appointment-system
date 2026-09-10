from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("wallet/", views.wallet_detail, name="wallet_detail"),
    path("wallet/charge/", views.wallet_charge, name="wallet_charge"),
    path("wallet/transactions/", views.wallet_transactions, name="wallet_transactions"),
]
