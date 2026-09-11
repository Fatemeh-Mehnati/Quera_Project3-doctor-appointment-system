from django.db import models

class Specialty(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True,
    )
    description = models.TextField(
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Doctor(models.Model):
    class VerificationStatus(models.TextChoices):
        PENDING = "PENDING", "Pending"
        APPROVED = "APPROVED", "Approved"
        REJECTED = "REJECTED", "Rejected"

    user = models.OneToOneField(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='doctor',
    )
    verification_status = models.CharField(
        max_length=20,
        choices=VerificationStatus,
        default=VerificationStatus.PENDING,
    )
    verified_by_user = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='doctor_verified',
    )
    verified_at = models.DateTimeField(
        null=True,
        blank=True,
    )
    verification_note = models.TextField(
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Doctor:{self.user.email}"


class DoctorSpecialty(models.Model):
    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.CASCADE,
        related_name='doctor_specialties',
    )
    specialty = models.ForeignKey(
        Specialty,
        on_delete=models.CASCADE,
        related_name='doctor_specialties',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["doctor", "specialty"],
                name="unique_specialty_per_doctor",
            ),
        ]

    def __str__(self):
        return f"{self.doctor} - {self.specialty}"


class Review(models.Model):
    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.CASCADE,
        related_name="reviews",
    )
    patient_user = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="doctor_reviews",
    )
    rating = models.PositiveSmallIntegerField()
    comment = models.TextField(
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            # هر کاربر فقط یک نظر برای هر پزشک می‌تواند ثبت کند؛ ثبت دوباره
            # همان نظر قبلی را به‌روزرسانی می‌کند (نگاه کنید به
            # submit_review در views.py که از update_or_create استفاده می‌کند).
            models.UniqueConstraint(
                fields=["doctor", "patient_user"],
                name="unique_review_per_patient_per_doctor",
            ),
            models.CheckConstraint(
                condition=models.Q(rating__gte=1, rating__lte=5),
                name="review_rating_between_1_and_5",
            ),
        ]

    def __str__(self):
        return f"{self.patient_user.email} -> {self.doctor} ({self.rating}★)"