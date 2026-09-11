from django import forms
from django.contrib.auth import get_user_model
from .models import Doctor, Specialty, DoctorSpecialty

User = get_user_model()


class DoctorCreateForm(forms.ModelForm):
    specialties = forms.ModelMultipleChoiceField(
        queryset=Specialty.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = Doctor
        fields = ["user", "verification_status", "verification_note"]

    def save(self, commit=True):
        doctor = super().save(commit=commit)
        if commit:
            selected_specialties = self.cleaned_data.get("specialties")
            if selected_specialties:
                DoctorSpecialty.objects.filter(doctor=doctor).exclude(
                    specialty__in=selected_specialties
                ).delete()
                for specialty in selected_specialties:
                    DoctorSpecialty.objects.get_or_create(
                        doctor=doctor,
                        specialty=specialty,
                    )
        return doctor


class DoctorSearchForm(forms.Form):
    query = forms.CharField(required=False)
    specialty = forms.ModelChoiceField(
        queryset=Specialty.objects.all(),
        required=False,
    )


class DoctorReviewForm(forms.Form):
    rating = forms.IntegerField(
        min_value=1,
        max_value=5,
        label="امتیاز",
        widget=forms.RadioSelect(choices=[(i, i) for i in range(1, 6)]),
    )
    comment = forms.CharField(
        widget=forms.Textarea(
            attrs={"rows": 4, "placeholder": "تجربه‌ی خود را از این ویزیت بنویسید (اختیاری)"}
        ),
        required=False,
        label="نظر شما",
    )