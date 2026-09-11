import random
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from faker import Faker

from doctors.models import Doctor, Specialty, DoctorSpecialty
from accounts.models import Role, UserRole
# ✅ ایمپورت مدل‌های تصحیح‌شده
from appointments.models import TimeSlot, SlotPriceHistory

User = get_user_model()

SPECIALTIES = [
    'Cardiology', 'Dermatology', 'Neurology', 'Pediatrics',
    'Orthopedics', 'Psychiatry', 'General Practice', 'Ophthalmology',
    'Gynecology', 'Oncology', 'Urology', 'Radiology',
]


class Command(BaseCommand):
    help = 'ایجاد پزشکان ساختگی همراه با اسلات‌های زمانی و هزینه‌های ویزیت'

    def add_arguments(self, parser):
        parser.add_argument('count', type=int, help='تعداد پزشکان جهت اضافه شدن')

    def handle(self, *args, **options):
        count = options['count']
        fake = Faker('en_US')

        doctor_role, _ = Role.objects.get_or_create(name='DOCTOR')

        created_count = 0
        total_slots_created = 0
        attempts = 0
        max_attempts = count * 10

        while created_count < count and attempts < max_attempts:
            attempts += 1

            phone = fake.unique.msisdn()
            email = fake.unique.email()
            first_name = fake.first_name()
            last_name = fake.last_name()

            if User.objects.filter(phone=phone).exists() or User.objects.filter(email=email).exists():
                continue

            # ایجاد کاربر
            user = User.objects.create_user(
                email=email,
                phone=phone,
                first_name=first_name,
                last_name=last_name,
                password='Password123!'
            )

            UserRole.objects.get_or_create(user=user, role=doctor_role)

            doctor = Doctor.objects.create(
                user=user,
                verification_status='APPROVED',
            )

            specialty_name = random.choice(SPECIALTIES)
            specialty, _ = Specialty.objects.get_or_create(name=specialty_name)
            DoctorSpecialty.objects.get_or_create(doctor=doctor, specialty=specialty)

            created_count += 1

            now = timezone.now()
            for day_offset in range(1, 15):
                target_date = (now + timedelta(days=day_offset)).date()
                price = random.choice([50000, 75000, 100000, 120000, 150000, 200000])

                start_hours = [9, 11, 14, 16]
                selected_hours = random.sample(start_hours, k=random.randint(2, 4))

                for hour in selected_hours:
                    start_dt = timezone.make_aware(
                        datetime.combine(
                            target_date,
                            datetime.min.time().replace(hour=hour, minute=0)
                        )
                    )
                    end_dt = start_dt + timedelta(minutes=30)

                    # ✅ اصلاح ساختار TimeSlot
                    time_slot = TimeSlot.objects.create(
                        doctor=doctor,
                        start_at=start_dt,
                        end_at=end_dt,
                    )
                    total_slots_created += 1

                    # ✅ ایجاد سابقه قیمت برای اسلات مربوطه
                    SlotPriceHistory.objects.create(
                        time_slot=time_slot,
                        amount=price,
                        created_by_user=user,
                    )

        self.stdout.write(
            self.style.SUCCESS(
                f'{created_count} doctor(s) and {total_slots_created} slot(s) created successfully.'
            )
        )