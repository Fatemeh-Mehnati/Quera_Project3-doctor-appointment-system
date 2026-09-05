from django.db import models

class Specialty(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Doctor(models.Model):
    user = models.OneToOneField(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='doctor',
    )
    verification_status = models.CharField(max_length=100)
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

    def __str__(self):
        return f"{self.doctor} - {self.specialty}"