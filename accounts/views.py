import random
from datetime import datetime
from decimal import Decimal, InvalidOperation

from django.contrib.auth import (
    get_user_model,
    login,
    authenticate,
    logout,
)
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.contrib import messages
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.utils import timezone

from .forms import (
    OTPRequestForm,
    OTPVerifyForm,
    UserRegistrationForm,
    LoginForm,
)

from .models import Wallet, WalletTransaction

User = get_user_model()


def request_otp(request):
    if request.method == "POST":
        form = OTPRequestForm(request.POST)

        if form.is_valid():
            email = form.cleaned_data['email']

            # Check if user exists
            user_exists = User.objects.filter(email=email).exists()

            if user_exists:
                code = str(random.randint(100000, 999999))

                request.session['otp_code'] = code
                request.session['otp_email'] = email
                request.session['otp_created_at'] = timezone.now().isoformat()
                request.session['otp_attempts'] = 0

                send_mail(
                    'Your OTP Code',
                    f'Your OTP Code is {code}',
                    None,
                    [email],
                )

            # Same response whether email exists or not
            return redirect('accounts:verify_otp')

    else:
        form = OTPRequestForm()

    return render(
        request,
        'accounts/request_otp.html',
        {'form': form}
    )


def verify_otp(request):
    if request.method == "POST":
        form = OTPVerifyForm(request.POST)

        if form.is_valid():
            email = form.cleaned_data['email']
            code = form.cleaned_data['code']

            saved_code = request.session.get('otp_code')
            saved_email = request.session.get('otp_email')
            created_at = request.session.get('otp_created_at')
            attempts = request.session.get('otp_attempts', 0)

            # There is no OTP
            if not saved_code or not saved_email or not created_at:
                form.add_error(
                    None,
                    'کد OTP معتبر نیست یا منقضی شده است'
                )
                return render(
                    request,
                    'accounts/verify_otp.html',
                    {'form': form}
                )

            # Email must be the same email that requested OTP
            if email != saved_email:
                form.add_error(
                    None,
                    'کد OTP معتبر نیست'
                )
                return render(
                    request,
                    'accounts/verify_otp.html',
                    {'form': form}
                )

            # Check if OTP has expired after 2 minutes
            created_at = datetime.fromisoformat(created_at)
            elapsed_time = timezone.now() - created_at

            if elapsed_time.total_seconds() > 120:
                request.session.pop('otp_code', None)
                request.session.pop('otp_email', None)
                request.session.pop('otp_created_at', None)
                request.session.pop('otp_attempts', None)

                form.add_error(
                    None,
                    'کد OTP منقضی شده است'
                )
                return render(
                    request,
                    'accounts/verify_otp.html',
                    {'form': form}
                )

            # Attempts limit
            if attempts >= 3:
                request.session.pop('otp_code', None)
                request.session.pop('otp_email', None)
                request.session.pop('otp_created_at', None)
                request.session.pop('otp_attempts', None)

                form.add_error(
                    None,
                    'تعداد تلاش های مجاز تمام شده است'
                )
                return render(
                    request,
                    'accounts/verify_otp.html',
                    {'form': form}
                )

            # OTP check
            if code != saved_code:
                request.session['otp_attempts'] = attempts + 1

                form.add_error(
                    None,
                    'کد OTP اشتباه است'
                )
                return render(
                    request,
                    'accounts/verify_otp.html',
                    {'form': form}
                )

            # User login
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                form.add_error(
                    None,
                    'کد OTP معتبر نیست'
                )
                return render(
                    request,
                    'accounts/verify_otp.html',
                    {'form': form}
                )

            # OTP is one-time use
            request.session.pop('otp_code', None)
            request.session.pop('otp_email', None)
            request.session.pop('otp_created_at', None)
            request.session.pop('otp_attempts', None)

            login(request, user)

            return redirect('accounts:profile')

    else:
        form = OTPVerifyForm()

    return render(
        request,
        'accounts/verify_otp.html',
        {'form': form}
    )


def register(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)

            return redirect('accounts:profile')

    else:
        form = UserRegistrationForm()

    return render(
        request,
        'accounts/register.html',
        {'form': form}
    )


def user_login(request):
    if request.method == "POST":
        form = LoginForm(request.POST)

        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            user = authenticate(
                request,
                email=email,
                password=password,
            )

            if user is not None:
                login(request, user)
                return redirect('accounts:profile')

            form.add_error(
                None,
                'ایمیل یا رمز عبور اشتباه است'
            )

    else:
        form = LoginForm()

    return render(
        request,
        'accounts/login.html',
        {'form': form}
    )


def user_logout(request):
    logout(request)
    return redirect('accounts:login')


@login_required
def profile(request):
    return render(
        request,
        'accounts/profile.html',
    )

@login_required
def wallet(request):
    wallet, _ = Wallet.objects.get_or_create(
        user=request.user
    )

    return render(
        request,
        'accounts/wallet.html',
        {'wallet': wallet}
    )


@login_required
def deposit(request):
    if request.method != "POST":
        return redirect("accounts:wallet")

    try:
        amount = Decimal(request.POST.get("amount", "0"))
    except InvalidOperation:
        messages.error(request, "Invalid amount.")
        return redirect("accounts:wallet")

    if amount <= 0:
        messages.error(request, "Amount must be greater than zero.")
        return redirect("accounts:wallet")

    wallet, _ = Wallet.objects.get_or_create(
        user=request.user
    )

    with transaction.atomic():
        wallet.balance += amount
        wallet.save(update_fields=["balance"])

        WalletTransaction.objects.create(
            wallet=wallet,
            type="DEPOSIT",
            direction="IN",
            status="COMPLETED",
            amount=amount,
        )

    return redirect("accounts:wallet")


@login_required
def withdraw(request):
    if request.method != "POST":
        return redirect("accounts:wallet")

    try:
        amount = Decimal(request.POST.get("amount", "0"))
    except InvalidOperation:
        messages.error(request, "Invalid amount.")
        return redirect("accounts:wallet")

    if amount <= 0:
        messages.error(request, "Amount must be greater than zero.")
        return redirect("accounts:wallet")

    wallet, _ = Wallet.objects.get_or_create(
        user=request.user
    )

    if amount > wallet.balance:
        messages.error(request, "Insufficient balance.")
        return redirect("accounts:wallet")

    with transaction.atomic():
        wallet.balance -= amount
        wallet.save(update_fields=["balance"])

        WalletTransaction.objects.create(
            wallet=wallet,
            type="WITHDRAW",
            direction="OUT",
            status="COMPLETED",
            amount=amount,
        )

    return redirect("accounts:wallet")


@login_required
def transaction_history(request):
    wallet, _ = Wallet.objects.get_or_create(
        user=request.user
    )

    transactions = wallet.transactions.all().order_by("-created_at")

    return render(
        request,
        "accounts/transaction_history.html",
        {"transactions": transactions},
    )