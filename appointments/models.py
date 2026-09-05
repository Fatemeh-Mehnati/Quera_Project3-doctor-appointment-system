from django.db import models


class TimeSlot(models.Model):
    doctor = models.ForeignKey(
        'doctors.Doctor',
        on_delete=models.CASCADE,
        related_name='time_slots',
    )
    start_at = models.DateTimeField()
    end_at = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['doctor', 'start_at'],
                name='unique_doctor_start_time',
            )
        ]

    def __str__(self):
        return f"{self.doctor} - {self.start_at}"


class Appointment(models.Model):
    patient_user = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='appointments',
    )
    visit_slot = models.ForeignKey(
        TimeSlot,
        on_delete=models.PROTECT,
        related_name='appointments',
    )
    reserved_price = models.DecimalField(
        max_digits=18,
        decimal_places=2,
    )
    status = models.CharField(max_length=50)

    cancelled_by_user = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cancelled_appointments',
    )
    cancelled_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    completed_by_user = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='completed_appointments',
    )
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    no_show_marked_by_user = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='no_show_appointments',
    )
    no_show_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Appointment {self.id}"