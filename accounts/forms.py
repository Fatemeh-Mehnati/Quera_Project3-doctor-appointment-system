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
            raise forms.ValidationError("Email already registered")
        return email

    def clean_phone(self):
        phone = self.cleaned_data.get("phone")
        if phone and User.objects.filter(phone=phone).exists():
            raise forms.ValidationError("phone already registered")
        return phone


class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)


class OTPRequestForm(forms.Form):
    email = forms.EmailField()

class OTPVerifyForm(forms.Form):
    email = forms.EmailField()
    code = forms.CharField(max_length=10)


class WalletChargeForm(forms.Form):
    amount = forms.DecimalField(max_digits=18, decimal_places=2, min_value=0.01)

