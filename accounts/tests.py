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
        # 1. تنظیم کلاینت تست
        self.client = Client()

        # 2. ساخت داده‌های پایه
        self.patient_role = Role.objects.create(code=Role.Code.PATIENT, name="Patient")

        self.user = User.objects.create_user(
            email='test@example.com',
            password='password123',
            first_name='Test',
            last_name='User'
        )

        UserRole.objects.create(user=self.user, role=self.patient_role)
        self.wallet = Wallet.objects.create(user=self.user, balance=0)

    #  بخش اول: تست مدل‌ها و محدودیت‌ها

    def test_user_role_unique_constraint(self):
        """تست مدل: عدم امکان ثبت نقش تکراری برای یک کاربر"""
        with self.assertRaises(IntegrityError):
            UserRole.objects.create(user=self.user, role=self.patient_role)

    def test_wallet_balance_non_negative_constraint(self):
        """تست مدل: موجودی کیف پول نمی‌تواند منفی شود"""
        with self.assertRaises(IntegrityError):
            self.wallet.balance = Decimal('-10.00')
            self.wallet.save()


    # بخش دوم: تست منطق کیف پول

    def test_wallet_deposit_success(self):
        """تست منطق: واریز موفق به کیف پول و افزایش موجودی"""
        txn = self.wallet.deposit(Decimal('50000.00'), type="CHARGE")

        self.assertEqual(self.wallet.balance, Decimal('50000.00'))
        self.assertEqual(txn.amount, Decimal('50000.00'))
        self.assertEqual(txn.direction, "CREDIT")
        self.assertEqual(WalletTransaction.objects.count(), 1)

    def test_wallet_withdraw_success(self):
        """تست منطق: برداشت موفق از کیف پول"""
        self.wallet.deposit(Decimal('100000.00'))
        txn = self.wallet.withdraw(Decimal('40000.00'), type="PAYMENT")

        self.assertEqual(self.wallet.balance, Decimal('60000.00'))
        self.assertEqual(txn.amount, Decimal('40000.00'))
        self.assertEqual(txn.direction, "DEBIT")

    def test_wallet_withdraw_insufficient_balance(self):
        """تست منطق حساس: جلوگیری از برداشت در صورت موجودی ناکافی"""
        self.wallet.deposit(Decimal('20000.00'))
        with self.assertRaises(InsufficientBalanceError):
            self.wallet.withdraw(Decimal('50000.00'))


    # بخش سوم: تست فرم‌ها

    def test_user_registration_form_duplicate_email(self):
        """تست فرم: جلوگیری از ثبت‌نام با ایمیل تکراری"""
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
        """تست فرم: اعتبارسنجی حداقل مبلغ شارژ (کمتر از 0.01)"""
        form = WalletChargeForm(data={'amount': 0.00})
        self.assertFalse(form.is_valid())
        self.assertIn('amount', form.errors)

    #
    # بخش چهارم: تست ویوها

    def test_dashboard_access_unauthenticated(self):
        """تست ویو: ارجاع کاربر لاگین‌نکرده به صفحه لاگین"""
        url = reverse('accounts:dashboard')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url.lower())

    def test_dashboard_access_authenticated_and_template(self):
        """تست ویو: دسترسی کاربر لاگین‌کرده به داشبورد و تمپلیت صحیح"""
        self.client.login(email='test@example.com', password='password123')
        url = reverse('accounts:dashboard')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/dashboard.html')

    def test_wallet_charge_view_action(self):
        """تست ویو: انجام عملیات شارژ کیف پول از طریق درخواست POST"""
        self.client.login(email='test@example.com', password='password123')
        url = reverse('accounts:wallet_charge')

        response = self.client.post(url, {'amount': '150000.00'})

        # باید به wallet_detail ریدایرکت شود
        self.assertRedirects(response, reverse('accounts:wallet_detail'))

        # موجودی کیف پول باید ۱۵۰,۰۰۰ تومان افزایش یافته باشد
        self.wallet.refresh_from_db()
        self.assertEqual(self.wallet.balance, Decimal('150000.00'))