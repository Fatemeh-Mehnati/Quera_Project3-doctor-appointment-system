from django import forms
from .models import TimeSlot, Appointment


class TimeSlotForm(forms.ModelForm):
    class Meta:
        model = TimeSlot
        fields = ["doctor", "start_at", "end_at", "is_active"]
        widgets = {
            "start_at": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "end_at": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_at = cleaned_data.get("start_at")
        end_at = cleaned_data.get("end_at")
        if start_at and end_at and start_at >= end_at:
            raise forms.ValidationError("زمان شروع باید قبل از زمان پایان باشد")
        return cleaned_data


class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ["visit_slot"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["visit_slot"].queryset = TimeSlot.objects.filter(
            is_active=True,
            appointment__isnull=True,
        )