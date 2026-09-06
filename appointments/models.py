from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import F, Q


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

    def clean(self):
        super().clean()

        overlapping_slots = TimeSlot.objects.filter(
            doctor=self.doctor,
            start_at__lt=self.end_at,
            end_at__gt=self.start_at,
        )

        if self.pk:
            overlapping_slots = overlapping_slots.exclude(pk=self.pk)

        if overlapping_slots.exists():
            raise ValidationError(
                "This time slot overlaps with another time slot for this doctor."
            )

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=Q(start_at__lt=F("end_at")),
                name="timeslot_start_before_end",
            ),
        ]

    def __str__(self):
        return f"{self.doctor} - {self.start_at} to {self.end_at}"


class SlotPriceHistory(models.Model):
    time_slot = models.ForeignKey(
        TimeSlot,
        on_delete=models.CASCADE,
        related_name="price_history",
    )

    amount = models.DecimalField(
        max_digits=18,
        decimal_places=2,
    )

    effective_at = models.DateTimeField(
        auto_now_add=True,
    )

    created_by_user = models.ForeignKey(
        "accounts.User",
        on_delete=models.PROTECT,
        related_name="created_slot_prices",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ["-effective_at"]

        constraints = [
            models.CheckConstraint(
                condition=Q(amount__gt=0),
                name="slot_price_amount_positive",
            ),
        ]

    def __str__(self):
        return f"{self.time_slot} - {self.amount}"


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