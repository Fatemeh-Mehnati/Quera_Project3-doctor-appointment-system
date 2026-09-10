import random
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from faker import Faker

from doctors.models import Doctor
from accounts.models import Role, UserRole
from appointments.models import TimeSlot

User = get_user_model()

SPECIALTIES = [
    'Cardiology',
    'Dermatology',
    'Neurology',
    'Pediatrics',
    'Orthopedics',
    'Psychiatry',
    'General Practice',
    'Ophthalmology',
    'Gynecology',
    'Oncology',
    'Urology',
    'Radiology',
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
            license_num = f"MC-{fake.unique.random_number(digits=6, fix_len=True)}"
            first_name = fake.first_name()
            last_name = fake.last_name()

            if User.objects.filter(phone_number=phone).exists():
                continue

            # ایجاد کاربر
            user = User.objects.create_user(
                phone_number=phone,
                first_name=first_name,
                last_name=last_name,
                password='Password123!'
            )

            UserRole.objects.get_or_create(user=user, role=doctor_role)

            specialty = fake.random_element(elements=SPECIALTIES)
            bio = f"Dr. {first_name} {last_name} is a specialist in {specialty} with extensive medical practice."

            # ایجاد پزشک
            doctor = Doctor.objects.create(
                user=user,
                medical_license_number=license_num,
                specialty=specialty,
                bio=bio,
                verification_status='APPROVED'
            )

            created_count += 1

            # تولید اسلات‌های زمانی و قیمت برای ۱۴ روز آینده
            now = timezone.now()
            for day_offset in range(1, 15):  # از فردا تا ۱۴ روز بعد
                target_date = (now + timedelta(days=day_offset)).date()

                # تعیین هزینه ویزیت تصادفی برای پزشک (بین ۵۰,۰۰۰ تا ۲۰۰,۰۰۰ تومان/واحد)
                price = random.choice([50000, 75000, 100000, 120000, 150000, 200000])

                # ساعات کاری تصادفی (مثلاً ۳ اسلات در روزهای کاری)
                start_hours = [9, 11, 14, 16]
                selected_hours = random.sample(start_hours, k=random.randint(2, 4))

                for hour in selected_hours:
                    start_dt = timezone.make_aware(
                        datetime.combine(target_date, datetime.min.time().replace(hour=hour, minute=0))
                    )
                    end_dt = start_dt + timedelta(minutes=30)

                    TimeSlot.objects.create(
                        doctor=doctor,
                        start_time=start_dt,
                        end_time=end_dt,
                        price=price,
                        is_booked=False
                    )
                    total_slots_created += 1

        self.stdout.write(
            self.style.SUCCESS(
                f' {created_count}: {total_slots_created} .'
            )
        )