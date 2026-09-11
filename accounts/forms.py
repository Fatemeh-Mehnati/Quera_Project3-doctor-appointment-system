from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

User = get_user_model()


class UserRegistrationForm(UserCreationForm):
    phone = forms.CharField(required=False)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ["email", "first_name", "last_name", "phone"]

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("این ایمیل قبلاً ثبت شده است")
        return email

    def clean_phone(self):
        phone = self.cleaned_data.get("phone")
        if phone and User.objects.filter(phone=phone).exists():
            raise forms.ValidationError("این شماره تلفن قبلاً ثبت شده است")
        return phone


class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)


class OTPRequestForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                "class": "w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500",
                "placeholder": "your@email.com",
            }
        )
    )

class OTPVerifyForm(forms.Form):
    email = forms.EmailField()
    code = forms.CharField(max_length=10)


class WalletChargeForm(forms.Form):
    amount = forms.DecimalField(max_digits=18, decimal_places=2, min_value=0.01)

