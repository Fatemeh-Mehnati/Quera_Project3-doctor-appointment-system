from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.utils import timezone
from .managers import UserManager


class InsufficientBalanceError(Exception):
    """وقتی موجودی کیف پول برای برداشت کافی نباشد raise می‌شود."""


class User(AbstractUser):
    username = None

    email = models.EmailField(max_length=255,unique=True)

    phone = models.CharField(
        max_length=32,
        unique=True,
        null=True,
        blank=True,
    )

    first_name = models.CharField(
        max_length=100,
    )

    last_name = models.CharField(
        max_length=100,
    )

    created_by_user = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_users',
    )

    roles = models.ManyToManyField(
        "Role",
        through="UserRole",
        through_fields=("user", "role"),
        related_name="users",
        blank=True,
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


class Role(models.Model):
    class Code(models.TextChoices):
        PATIENT = "PATIENT", "Patient"
        DOCTOR = "DOCTOR", "Doctor"
        ADMIN = "ADMIN", "Admin"

    code = models.CharField(
        max_length=50,
        choices=Code,
        unique=True,
    )

    name = models.CharField(
        max_length=100,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    def __str__(self):
        return self.name


class UserRole(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="role_assignments",
    )

    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        related_name="user_assignments",
    )

    assigned_by_user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_role_records",
    )

    assigned_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "role"],
                name="unique_role_per_user",
            ),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.role.code}"



class Wallet(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='wallets'
    )
    balance = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default = 0
    )
    held_balance = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        default = 0
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(balance__gte=0),
                name="wallet_balance_non_negative",
            ),
        ]

    def __str__(self):
        return f"{self.user.email} - Wallet"

    def deposit(self, amount, *, type="CHARGE", external_reference=None, payment=None):

        if amount <= 0:
            raise ValidationError("مبلغ واریزی باید بزرگ‌تر از صفر باشد.")

        with transaction.atomic():
            wallet = Wallet.objects.select_for_update().get(pk=self.pk)
            wallet.balance += amount
            wallet.save(update_fields=["balance", "updated_at"])

            txn = wallet.transactions.create(
                payment=payment,
                type=type,
                direction="CREDIT",
                status="COMPLETED",
                amount=amount,
                external_reference=external_reference,
                completed_at=timezone.now(),
            )

        self.refresh_from_db(fields=["balance"])
        return txn

    def withdraw(self, amount, *, type="PAYMENT", external_reference=None, payment=None):

        if amount <= 0:
            raise ValidationError("مبلغ برداشت باید بزرگ‌تر از صفر باشد.")

        with transaction.atomic():
            wallet = Wallet.objects.select_for_update().get(pk=self.pk)
            if wallet.balance < amount:
                raise InsufficientBalanceError("موجودی کیف پول کافی نیست.")

            wallet.balance -= amount
            wallet.save(update_fields=["balance", "updated_at"])

            txn = wallet.transactions.create(
                payment=payment,
                type=type,
                direction="DEBIT",
                status="COMPLETED",
                amount=amount,
                external_reference=external_reference,
                completed_at=timezone.now(),
            )

        self.refresh_from_db(fields=["balance"])
        return txn


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
        return f"Payment {self.pk} - {self.amount}"


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
        return f"Transaction {self.pk} - {self.amount}"
