from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError
from decimal import Decimal
from .models import Wallet, Role, UserRole, InsufficientBalanceError, WalletTransaction
from .forms import UserRegistrationForm, WalletChargeForm

User = get_user_model()

class AccountsAppTests(TestCase):
    def setUp(self):
        self.client = Client()

        self.patient_role, _ = Role.objects.get_or_create(
            code=Role.Code.PATIENT,
            defaults={'name': 'Patient'}
        )
        self.user = User.objects.create_user(
            email='test@example.com',
            password='password123',
            first_name='Test',
            last_name='User'
        )

        UserRole.objects.get_or_create(user=self.user, role=self.patient_role)
        self.wallet, _ = Wallet.objects.get_or_create(user=self.user, defaults={'balance': 0})



    def test_user_role_unique_constraint(self):
        with self.assertRaises(IntegrityError):
            UserRole.objects.create(user=self.user, role=self.patient_role)

    def test_wallet_balance_non_negative_constraint(self):
        with self.assertRaises(IntegrityError):
            self.wallet.balance = Decimal('-10.00')
            self.wallet.save()

    def test_wallet_deposit_success(self):
        txn = self.wallet.deposit(Decimal('50000.00'), type="CHARGE")
        self.assertEqual(self.wallet.balance, Decimal('50000.00'))
        self.assertEqual(txn.amount, Decimal('50000.00'))
        self.assertEqual(txn.direction, "CREDIT")
        self.assertEqual(WalletTransaction.objects.count(), 1)

    def test_wallet_withdraw_success(self):
        self.wallet.deposit(Decimal('100000.00'))
        txn = self.wallet.withdraw(Decimal('40000.00'), type="PAYMENT")
        self.assertEqual(self.wallet.balance, Decimal('60000.00'))
        self.assertEqual(txn.amount, Decimal('40000.00'))
        self.assertEqual(txn.direction, "DEBIT")

    def test_wallet_withdraw_insufficient_balance(self):
        self.wallet.deposit(Decimal('20000.00'))
        with self.assertRaises(InsufficientBalanceError):
            self.wallet.withdraw(Decimal('50000.00'))

    def test_user_registration_form_duplicate_email(self):
        form_data = {
            'email': 'test@example.com',
            'first_name': 'Ali',
            'last_name': 'Rezai',
            'password1': 'password123',
            'password2': 'password123'
        }
        form = UserRegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
        self.assertEqual(form.errors['email'][0], "این ایمیل قبلاً ثبت شده است")

    def test_wallet_charge_form_invalid_amount(self):
        form = WalletChargeForm(data={'amount': 0.00})
        self.assertFalse(form.is_valid())
        self.assertIn('amount', form.errors)

    def test_dashboard_access_unauthenticated(self):
        url = reverse('accounts:dashboard')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url.lower())

    def test_dashboard_access_authenticated_and_template(self):
        self.client.login(email='test@example.com', password='password123')
        url = reverse('accounts:dashboard')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/dashboard.html')

    def test_wallet_charge_view_action(self):
        self.client.login(email='test@example.com', password='password123')
        url = reverse('accounts:wallet_charge')
        response = self.client.post(url, {'amount': '150000.00'})

        self.assertRedirects(response, reverse('accounts:wallet_detail'))
        self.wallet.refresh_from_db()
        self.assertEqual(self.wallet.balance, Decimal('150000.00'))