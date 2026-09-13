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

        patient_role, _ = Role.objects.get_or_create(code=Role.Code.PATIENT, defaults={'name': 'Patient'})
        doctor_role, _ = Role.objects.get_or_create(code=Role.Code.DOCTOR, defaults={'name': 'Doctor'})
        admin_role, _ = Role.objects.get_or_create(code=Role.Code.ADMIN, defaults={'name': 'Admin'})

        self.patient = User.objects.create_user(
            email='patient@test.com',
            password='password123',
            first_name='Pat',
            last_name='ient'
        )
        UserRole.objects.get_or_create(user=self.patient, role=patient_role)

        self.poor_patient = User.objects.create_user(
            email='poor@test.com',
            password='password123',
            first_name='Poor',
            last_name='Patient'
        )
        UserRole.objects.get_or_create(user=self.poor_patient, role=patient_role)

        self.dr_user = User.objects.create_user(
            email='doctor@test.com',
            password='password123',
            first_name='Doc',
            last_name='Tor'
        )
        UserRole.objects.get_or_create(user=self.dr_user, role=doctor_role)

        self.admin = User.objects.create_user(
            email='admin@test.com',
            password='password123',
            first_name='Ad',
            last_name='Min'
        )
        UserRole.objects.get_or_create(user=self.admin, role=admin_role)

        self.wallet, _ = Wallet.objects.get_or_create(user=self.patient)
        self.wallet.balance = Decimal('500000.00')
        self.wallet.save()

        self.poor_wallet, _ = Wallet.objects.get_or_create(user=self.poor_patient)
        self.poor_wallet.balance = Decimal('10000.00')
        self.poor_wallet.save()

        self.doctor, _ = Doctor.objects.get_or_create(user=self.dr_user)
        for attr in ['verification_status', 'status']:
            if hasattr(self.doctor, attr):
                setattr(self.doctor, attr, 'APPROVED')
        if hasattr(self.doctor, 'is_active'):
            self.doctor.is_active = True
        if hasattr(self.doctor, 'is_approved'):
            self.doctor.is_approved = True
        self.doctor.save()

        now = timezone.now()
        self.slot = TimeSlot.objects.create(
            doctor=self.doctor,
            start_at=now + timedelta(days=1, hours=10),
            end_at=now + timedelta(days=1, hours=10, minutes=30),
            is_active=True
        )

        self.slot_price = Decimal('100000.00')
        SlotPriceHistory.objects.create(
            time_slot=self.slot,
            amount=self.slot_price,
            created_by_user=self.admin
        )

    def test_timeslot_overlapping_validation(self):
        now = timezone.now()
        overlapping_slot = TimeSlot(
            doctor=self.doctor,
            start_at=now + timedelta(days=1, hours=10, minutes=15),
            end_at=now + timedelta(days=1, hours=10, minutes=45),
            is_active=True
        )
        with self.assertRaises(ValidationError):
            overlapping_slot.clean()

    def test_timeslot_start_before_end_constraint(self):
        now = timezone.now()
        with self.assertRaises(IntegrityError):
            TimeSlot.objects.create(
                doctor=self.doctor,
                start_at=now + timedelta(hours=2),
                end_at=now + timedelta(hours=1),
            )

    def test_timeslot_form_validation(self):
        now = timezone.now()
        data_invalid = {
            'doctor': self.doctor.pk,
            'start_at': now + timedelta(hours=2),
            'end_at': now + timedelta(hours=1),
            'is_active': True
        }
        form = TimeSlotForm(data=data_invalid)
        self.assertFalse(form.is_valid())
        self.assertIn('__all__', form.errors)
        self.assertEqual(form.errors['__all__'][0], "زمان شروع باید قبل از زمان پایان باشد")

        data_valid = {
            'doctor': self.doctor.pk,
            'start_at': now + timedelta(hours=1),
            'end_at': now + timedelta(hours=2),
            'is_active': True
        }
        form_valid = TimeSlotForm(data=data_valid)
        self.assertTrue(form_valid.is_valid())

    def test_available_slots_view_unauthenticated(self):
        url = reverse('appointments:available_slots', args=[self.doctor.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url.lower())

    def test_available_slots_view_authenticated(self):
        self.client.login(email='patient@test.com', password='password123')
        url = reverse('appointments:available_slots', args=[self.doctor.pk])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'appointments/available_slots.html')
        self.assertIn('items', response.context)

    def test_booking_insufficient_balance(self):
        self.client.login(email='poor@test.com', password='password123')
        url = reverse('appointments:reserve', args=[self.slot.pk])

        response = self.client.post(url)
        self.assertEqual(Appointment.objects.count(), 0)
        self.assertRedirects(response, reverse('doctors:doctor_detail', args=[self.doctor.pk]), fetch_redirect_response=False)
        self.poor_wallet.refresh_from_db()
        self.assertEqual(self.poor_wallet.balance, Decimal('10000.00'))

    def test_booking_double_slot(self):
        Appointment.objects.create(
            patient_user=self.patient,
            visit_slot=self.slot,
            reserved_price=self.slot_price,
            status=Appointment.Status.RESERVED
        )

        self.client.login(email='poor@test.com', password='password123')
        url = reverse('appointments:reserve', args=[self.slot.pk])

        response = self.client.post(url)

        self.assertEqual(Appointment.objects.count(), 1)
        self.assertRedirects(response, reverse('doctors:doctor_detail', args=[self.doctor.pk]), fetch_redirect_response=False)

    def test_booking_success_sends_email(self):
        self.client.login(email='patient@test.com', password='password123')
        url = reverse('appointments:reserve', args=[self.slot.pk])

        mail.outbox = []
        response = self.client.post(url)
        self.assertRedirects(response, reverse('appointments:my_appointments'), fetch_redirect_response=False)
        self.assertEqual(Appointment.objects.count(), 1)
        appointment = Appointment.objects.first()
        self.assertEqual(appointment.patient_user, self.patient)
        self.wallet.refresh_from_db()
        expected_balance = Decimal('500000.00') - self.slot_price
        self.assertEqual(self.wallet.balance, expected_balance)
        if len(mail.outbox) > 0:
            self.assertEqual(mail.outbox[0].subject, "تاییدیه رزرو نوبت")
            self.assertIn(self.patient.email, mail.outbox[0].to)