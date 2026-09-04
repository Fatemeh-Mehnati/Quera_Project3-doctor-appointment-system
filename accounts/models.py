from django.contrib.auth.models import AbstractUser
from django.db import models
from .managers import UserManager


class User(AbstractUser):
    username = None

    email = models.EmailField(max_length=255,unique=True)

    phone = models.CharField(
        max_length=11,
        unique=True,
        null=True,
        blank=True,
    )
    created_by_user = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_users',
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        auto_now=True
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email


class Wallet(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='wallets'
    )
    balance = models.DecimalField(
        max_digits=18,
        decimal_places=2
    )
    held_balance = models.DecimalField(
        max_digits=18,
        decimal_places=2
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email} - Wallet"


class Payment(models.Model):
    reservation = models.ForeignKey(
        'appointments.Appointment',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='payments'
    )
    payer_wallet = models.ForeignKey(
        Wallet,
        on_delete=models.PROTECT,
        related_name='payments_made'
    )
    beneficiary_wallet = models.ForeignKey(
        Wallet,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='payments_received'
    )
    amount = models.DecimalField(
        max_digits=18,
        decimal_places=2
    )
    status = models.CharField(max_length=50)

    held_at = models.DateTimeField(null=True, blank=True)
    released_at = models.DateTimeField(null=True, blank=True)
    refunded_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Payment {self.id} - {self.amount}"


class WalletTransaction(models.Model):
    wallet = models.ForeignKey(
        Wallet,
        on_delete=models.CASCADE,
        related_name='transactions'
    )
    payment = models.ForeignKey(
        Payment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='transactions'
    )
    type = models.CharField(max_length=50)
    direction = models.CharField(max_length=50)
    status = models.CharField(max_length=50)

    amount = models.DecimalField(
        max_digits=18,
        decimal_places=2
    )
    external_reference = models.CharField(
        max_length=255,
        null=True,
        blank=True
    )
    failure_reason = models.TextField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(
        null=True,
        blank=True
    )

    def __str__(self):
        return f"Transaction {self.id} - {self.amount}"
