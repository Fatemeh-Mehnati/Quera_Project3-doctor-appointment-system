from django.test import TestCase, Client
from django.urls import reverse
from django.core import mail
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from accounts.models import Wallet, Role, UserRole
from doctors.models import Doctor
from .models import TimeSlot, SlotPriceHistory, Appointment
from .forms import TimeSlotForm

User = get_user_model()


class AppointmentsAppTests(TestCase):
    def setUp(self):
        self.client = Client()


        patient_role, _ = Role.objects.get_or_create(code=Role.Code.PATIENT, name="Patient")
        doctor_role, _ = Role.objects.get_or_create(code=Role.Code.DOCTOR, name="Doctor")
        admin_role, _ = Role.objects.get_or_create(code=Role.Code.ADMIN, name="Admin")


        self.patient = User.objects.create_user(email='patient@test.com', password='password123', first_name='Pat',
                                                last_name='ient')
        UserRole.objects.create(user=self.patient, role=patient_role)

        self.poor_patient = User.objects.create_user(email='poor@test.com', password='password123', first_name='Poor',
                                                     last_name='Patient')
        UserRole.objects.create(user=self.poor_patient, role=patient_role)

        self.dr_user = User.objects.create_user(email='doctor@test.com', password='password123', first_name='Doc',
                                                last_name='Tor')
        UserRole.objects.create(user=self.dr_user, role=doctor_role)

        self.admin = User.objects.create_user(email='admin@test.com', password='password123', first_name='Ad',
                                              last_name='Min')
        UserRole.objects.create(user=self.admin, role=admin_role)


        self.wallet = Wallet.objects.create(user=self.patient, balance=Decimal('500000.00'))  # پول کافی دارد
        self.poor_wallet = Wallet.objects.create(user=self.poor_patient, balance=Decimal('10000.00'))  # پول کافی ندارد

        # 4. ساخت دکتر
        self.doctor = Doctor.objects.create(user=self.dr_user)

        # 5. ساخت TimeSlot
        now = timezone.now()
        self.slot = TimeSlot.objects.create(
            doctor=self.doctor,
            start_at=now + timedelta(days=1, hours=10),
            end_at=now + timedelta(days=1, hours=10, minutes=30),
            is_active=True
        )

        # 6. ساخت قیمت برای بازه
        self.slot_price = Decimal('100000.00')
        SlotPriceHistory.objects.create(
            time_slot=self.slot,
            amount=self.slot_price,
            created_by_user=self.admin
        )


    # بخش اول: تست مدل‌ها و محدودیت‌ها

    def test_timeslot_overlapping_validation(self):
        """تست مدل: جلوگیری از ایجاد بازه زمانی همپوشانی‌دار برای یک پزشک (clean)"""
        now = timezone.now()
        overlapping_slot = TimeSlot(
            doctor=self.doctor,
            start_at=now + timedelta(days=1, hours=10, minutes=15),  # همپوشانی با self.slot
            end_at=now + timedelta(days=1, hours=10, minutes=45),
            is_active=True
        )
        with self.assertRaises(ValidationError):
            overlapping_slot.clean()

    def test_timeslot_start_before_end_constraint(self):
        """تست مدل: بررسی CheckConstraint برای اینکه شروع قبل از پایان باشد"""
        now = timezone.now()
        with self.assertRaises(IntegrityError):
            TimeSlot.objects.create(
                doctor=self.doctor,
                start_at=now + timedelta(hours=2),
                end_at=now + timedelta(hours=1),  # پایان قبل از شروع است
            )

    # بخش دوم: تست فرم‌ها

    def test_timeslot_form_validation(self):
        """تست فرم: اعتبارسنجی زمان شروع و پایان در TimeSlotForm"""
        now = timezone.now()
        data_invalid = {
            'doctor': self.doctor.pk,
            'start_at': now + timedelta(hours=2),
            'end_at': now + timedelta(hours=1),  # غلط
            'is_active': True
        }
        form = TimeSlotForm(data=data_invalid)
        self.assertFalse(form.is_valid())
        self.assertIn('__all__', form.errors)
        self.assertEqual(form.errors['__all__'][0], "زمان شروع باید قبل از زمان پایان باشد")

        data_valid = {
            'doctor': self.doctor.pk,
            'start_at': now + timedelta(hours=1),
            'end_at': now + timedelta(hours=2),  # درست
            'is_active': True
        }
        form_valid = TimeSlotForm(data=data_valid)
        self.assertTrue(form_valid.is_valid())

    # بخش سوم: تست ویوها و منطق‌های حساس

    def test_available_slots_view_unauthenticated(self):
        """تست ویو: کد وضعیت و عدم دسترسی کاربر لاگین‌نکرده"""
        url = reverse('appointments:available_slots', args=[self.doctor.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url.lower())

    def test_available_slots_view_authenticated(self):
        """تست ویو: دسترسی کاربر لاگین‌کرده و تمپلیت استفاده‌شده"""
        self.client.login(email='patient@test.com', password='password123')
        url = reverse('appointments:available_slots', args=[self.doctor.pk])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'appointments/available_slots.html')
        self.assertIn('items', response.context)

    def test_booking_insufficient_balance(self):
        """تست رزرو با موجودی ناکافی باید شکست بخورد"""
        self.client.login(email='poor@test.com', password='password123')
        url = reverse('appointments:reserve_appointment', args=[self.slot.pk])

        response = self.client.post(url)
        # چک میکنیم نوبتی ثبت نشده باشد
        self.assertEqual(Appointment.objects.count(), 0)
        # به صفحه دکتر ریدایرکت می‌شود
        self.assertRedirects(response, reverse('doctors:doctor_detail', args=[self.doctor.pk]))
        # چک کردن عدم کسر پول
        self.poor_wallet.refresh_from_db()
        self.assertEqual(self.poor_wallet.balance, Decimal('10000.00'))

    def test_booking_double_slot(self):
        """تست منطق حساس: رزرو دوباره یک بازه (جلوگیری از رزرو همزمان)"""
        # ابتدا کاربر اول نوبت را با موفقیت می‌گیرد
        Appointment.objects.create(
            patient_user=self.patient,
            visit_slot=self.slot,
            reserved_price=self.slot_price,
            status=Appointment.Status.RESERVED
        )

        # حالا کاربر دوم تلاش می‌کند همان نوبت را بگیرد
        self.client.login(email='poor@test.com', password='password123')
        url = reverse('appointments:reserve_appointment', args=[self.slot.pk])

        response = self.client.post(url)

        # فقط باید همان ۱ نوبت اول در سیستم باشد
        self.assertEqual(Appointment.objects.count(), 1)
        self.assertRedirects(response, reverse('doctors:doctor_detail', args=[self.doctor.pk]))

    def test_booking_success_sends_email(self):
        """تست رزرو موفق، کسر پول و ارسال ایمیل (تست mail.outbox)"""
        self.client.login(email='patient@test.com', password='password123')
        url = reverse('appointments:reserve_appointment', args=[self.slot.pk])

        # خالی کردن ایمیل‌های خروجی قبلی
        mail.outbox = []
        response = self.client.post(url)
        # 1. چک کردن ریدایرکت موفق
        self.assertRedirects(response, reverse('appointments:my_appointments'))
        # 2. چک کردن ایجاد نوبت
        self.assertEqual(Appointment.objects.count(), 1)
        appointment = Appointment.objects.first()
        self.assertEqual(appointment.patient_user, self.patient)
        # 3. چک کردن کسر پول
        self.wallet.refresh_from_db()
        expected_balance = Decimal('500000.00') - self.slot_price
        self.assertEqual(self.wallet.balance, expected_balance)
        # 4. تست ارسال ایمیل با outbox
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "تاییدیه رزرو نوبت")
        self.assertIn(self.patient.email, mail.outbox[0].to)