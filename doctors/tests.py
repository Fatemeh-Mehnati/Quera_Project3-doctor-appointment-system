from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError
from django.utils import timezone
from datetime import timedelta
from appointments.models import TimeSlot, Appointment
from .models import Specialty, Doctor, DoctorSpecialty, Review
from .forms import DoctorCreateForm, DoctorSearchForm, DoctorReviewForm

User = get_user_model()


class DoctorsAppTests(TestCase):
    def setUp(self):
        self.client = Client()

        self.dr_user = User.objects.create_user(
            email="doctor@test.com",
            password="password123",
            first_name="Ali",
            last_name="Rezai",
        )
        self.dr_pending_user = User.objects.create_user(
            email="pending_doc@test.com",
            password="password123",
            first_name="Hassan",
            last_name="Ahmadi",
        )
        self.patient_user = User.objects.create_user(
            email="patient@test.com",
            password="password123",
            first_name="Sara",
            last_name="Mohammadi",
        )

        self.doctor = Doctor.objects.create(
            user=self.dr_user,
            verification_status=Doctor.VerificationStatus.APPROVED,
        )
        self.pending_doctor = Doctor.objects.create(
            user=self.dr_pending_user,
            verification_status=Doctor.VerificationStatus.PENDING,
        )

        self.specialty = Specialty.objects.create(name="Cardiology")
        DoctorSpecialty.objects.create(doctor=self.doctor, specialty=self.specialty)

    def test_specialty_unique_name(self):
        with self.assertRaises(IntegrityError):
            Specialty.objects.create(name="Cardiology")

    def test_unique_specialty_per_doctor_constraint(self):
        with self.assertRaises(IntegrityError):
            DoctorSpecialty.objects.create(
                doctor=self.doctor, specialty=self.specialty
            )

    def test_review_rating_check_constraint(self):
        with self.assertRaises(IntegrityError):
            Review.objects.create(
                doctor=self.doctor,
                patient_user=self.patient_user,
                rating=6,
                comment="تست امتیاز غیرمجاز",
            )

    def test_doctor_create_form_saves_specialties(self):
        new_doc_user = User.objects.create_user(
            email="newdoc@test.com", password="password123"
        )
        form_data = {
            "user": new_doc_user.pk,
            "verification_status": Doctor.VerificationStatus.APPROVED,
            "verification_note": "Approved by admin",
            "specialties": [self.specialty.pk],
        }
        form = DoctorCreateForm(data=form_data)
        self.assertTrue(form.is_valid())
        saved_doctor = form.save()

        self.assertEqual(saved_doctor.doctor_specialties.count(), 1)
        self.assertEqual(
            saved_doctor.doctor_specialties.first().specialty, self.specialty
        )

    def test_doctor_review_form_validation(self):
        invalid_form = DoctorReviewForm(data={"rating": 10, "comment": "عالی"})
        self.assertFalse(invalid_form.is_valid())

        valid_form = DoctorReviewForm(data={"rating": 5, "comment": "عالی"})
        self.assertTrue(valid_form.is_valid())

    def test_doctor_list_shows_only_approved_doctors(self):
        url = reverse("doctors:doctor_list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "doctors/doctor_list.html")

        doctors_in_ctx = response.context["doctors"]
        self.assertIn(self.doctor, doctors_in_ctx)
        self.assertNotIn(self.pending_doctor, doctors_in_ctx)

    def test_doctor_detail_view_approved_vs_pending(self):
        approved_url = reverse("doctors:doctor_detail", args=[self.doctor.pk])
        response = self.client.get(approved_url)
        self.assertEqual(response.status_code, 200)

        pending_url = reverse("doctors:doctor_detail", args=[self.pending_doctor.pk])
        response_pending = self.client.get(pending_url)
        self.assertEqual(response_pending.status_code, 404)

    def test_submit_review_denied_without_completed_visit(self):
        self.client.login(email="patient@test.com", password="password123")
        url = reverse("doctors:submit_review", args=[self.doctor.pk])
        response = self.client.post(url, {"rating": 5, "comment": "عالی بود"})
        self.assertRedirects(
            response, reverse("doctors:doctor_detail", args=[self.doctor.pk])
        )
        self.assertEqual(Review.objects.count(), 0)

    def test_submit_review_success_and_update_with_completed_visit(self):
        now = timezone.now()
        slot = TimeSlot.objects.create(
            doctor=self.doctor,
            start_at=now - timedelta(days=2),
            end_at=now - timedelta(days=2, hours=-1),
            is_active=True,
        )
        Appointment.objects.create(
            patient_user=self.patient_user,
            visit_slot=slot,
            reserved_price=100000,
            status=Appointment.Status.COMPLETED,
        )

        self.client.login(email="patient@test.com", password="password123")
        url = reverse("doctors:submit_review", args=[self.doctor.pk])

        response = self.client.post(url, {"rating": 4, "comment": "خوب بود"})
        self.assertRedirects(
            response, reverse("doctors:doctor_detail", args=[self.doctor.pk])
        )
        self.assertEqual(Review.objects.count(), 1)
        review = Review.objects.first()
        self.assertEqual(review.rating, 4)
        self.assertEqual(review.comment, "خوب بود")

        self.client.post(url, {"rating": 5, "comment": "عالی شد"})

        self.assertEqual(Review.objects.count(), 1)
        review.refresh_from_db()
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.comment, "عالی شد")