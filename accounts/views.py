from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import redirect, render
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone
import random
from django.contrib.auth import get_user_model

from .forms import (
    LoginForm,
    OTPRequestForm,
    OTPVerifyForm,
    UserRegistrationForm,
    WalletChargeForm,
)
from .models import Wallet

User = get_user_model()

TRANSACTIONS_PER_PAGE = 20


def _otp_resend_wait_seconds(request):
    """
    ثانیه‌های باقی‌مانده تا مجاز بودن درخواست دوباره‌ی OTP.

    اگر OTPای در session نباشد یا کول‌داون تمام شده باشد صفر برمی‌گردد.
    """
    otp_created_at = request.session.get("otp_created_at")
    if not otp_created_at:
        return 0

    elapsed = timezone.now().timestamp() - otp_created_at
    remaining = settings.OTP_RESEND_COOLDOWN_SECONDS - elapsed
    return max(0, int(remaining))


def _generate_and_send_otp(request, email):
    """کد جدید می‌سازد، در session ذخیره و از طریق ایمیل ارسال می‌کند."""
    otp = str(random.randint(100000, 999999))

    request.session["otp_email"] = email
    request.session["otp_code"] = otp
    request.session["otp_created_at"] = timezone.now().timestamp()

    send_mail(
        subject="Your login code",
        message=f"Your login code: {otp}",
        from_email=None,
        recipient_list=[email],
    )


def signup_view(request):

    if request.user.is_authenticated:
        return redirect("accounts:dashboard")

    if request.method == "POST":
        form = UserRegistrationForm(request.POST)

        if form.is_valid():
            user = form.save()
            auth_login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request, "ثبت‌نام شما با موفقیت انجام شد. خوش آمدید!")
            return redirect("accounts:dashboard")

    else:
        form = UserRegistrationForm()

    return render(
        request,
        "accounts/signup.html",
        {"form": form},
    )


def otp_request_view(request):
    """
    درخواست کد OTP.

    این view هم می‌تواند از صفحه OTP جداگانه استفاده شود
    و هم از حالت ورود با OTP در صفحه Login.
    """

    if request.user.is_authenticated:
        return redirect("accounts:dashboard")

    if request.method == "POST":
        form = OTPRequestForm(request.POST)

        if form.is_valid():
            email = form.cleaned_data["email"]

            # بررسی اینکه کاربر با این ایمیل وجود دارد
            user = User.objects.filter(email=email).first()

            if user is None:
                form.add_error(
                    "email",
                    "No account was found with this email."
                )
            else:
                wait_seconds = _otp_resend_wait_seconds(request)

                if wait_seconds > 0:
                    form.add_error(
                        None,
                        f"Please wait {wait_seconds} seconds before requesting a new code."
                    )
                else:
                    _generate_and_send_otp(request, email)

                    # رفتن به صفحه تأیید OTP
                    return redirect("accounts:otp_verify")

    else:
        form = OTPRequestForm()

    return render(
        request,
        "accounts/otp_request.html",
        {"form": form, "resend_wait_seconds": _otp_resend_wait_seconds(request)},
    )


def otp_verify_view(request):
    """
    تأیید کد OTP و ورود کاربر.
    """

    if request.user.is_authenticated:
        return redirect("accounts:dashboard")

    if request.method == "POST":
        form = OTPVerifyForm(request.POST)

        if form.is_valid():
            email = form.cleaned_data["email"]
            code = form.cleaned_data["code"]

            # اطلاعات OTP از session
            otp_email = request.session.get("otp_email")
            otp_code = request.session.get("otp_code")
            otp_created_at = request.session.get("otp_created_at")

            # بررسی وجود OTP
            if not otp_email or not otp_code or not otp_created_at:

                form.add_error(
                    None,
                    "This code is invalid or has expired."
                )

            # بررسی ایمیل
            elif email != otp_email:

                form.add_error(
                    "email",
                    "This email doesn't match the one the code was sent to."
                )

            # بررسی زمان انقضا
            elif (
                timezone.now().timestamp() - otp_created_at
                > settings.OTP_EXPIRY_SECONDS
            ):

                form.add_error(
                    None,
                    "This code has expired."
                )

            # بررسی کد
            elif code != otp_code:

                form.add_error(
                    "code",
                    "Incorrect code."
                )

            else:
                # پیدا کردن کاربر
                user = User.objects.filter(email=email).first()

                if user is None:

                    form.add_error(
                        None,
                        "Your login details are invalid."
                    )

                else:
                    auth_login(request, user, backend='django.contrib.auth.backends.ModelBackend')

                    # پاک کردن اطلاعات OTP از session
                    request.session.pop("otp_email", None)
                    request.session.pop("otp_code", None)
                    request.session.pop("otp_created_at", None)

                    # انتقال به داشبورد
                    return redirect("accounts:dashboard")

    else:
        form = OTPVerifyForm(
            initial={
                "email": request.session.get("otp_email", "")
            }
        )

    return render(
        request,
        "accounts/otp_verify.html",
        {
            "form": form,
            "resend_wait_seconds": _otp_resend_wait_seconds(request),
            "otp_email": request.session.get("otp_email", ""),
        },
    )


def login_view(request):
    """
    صفحه Login با دو روش ورود:

    1. Email + Password
    2. Email + OTP

    حالت ورود از طریق فیلد hidden به نام login_method
    مشخص می‌شود.
    """

    if request.user.is_authenticated:
        return redirect("accounts:dashboard")

    next_url = request.GET.get("next") or request.POST.get("next")

    if request.method == "POST":

        login_method = request.POST.get("login_method", "password")

        # ---------------------------------
        # LOGIN WITH OTP
        # ---------------------------------
        if login_method == "otp":

            form = OTPRequestForm(request.POST)

            if form.is_valid():

                email = form.cleaned_data["email"]

                # بررسی وجود کاربر
                user = User.objects.filter(email=email).first()

                if user is None:

                    form.add_error(
                        "email",
                        "No account was found with this email."
                    )

                else:
                    wait_seconds = _otp_resend_wait_seconds(request)

                    if wait_seconds > 0:
                        form.add_error(
                            None,
                            f"Please wait {wait_seconds} seconds before requesting a new code."
                        )
                    else:
                        # نگه داشتن next برای بعد از login
                        if next_url:
                            request.session["otp_next"] = next_url

                        _generate_and_send_otp(request, email)

                        # رفتن به صفحه تأیید OTP
                        return redirect("accounts:otp_verify")

        # ---------------------------------
        # LOGIN WITH PASSWORD
        # ---------------------------------
        else:

            form = LoginForm(request.POST)

            if form.is_valid():

                email = form.cleaned_data["email"]
                password = form.cleaned_data["password"]

                user = authenticate(
                    request,
                    username=email,
                    password=password,
                )

                if user is not None:

                    auth_login(request, user)

                    return redirect(
                        next_url or "accounts:dashboard"
                    )

                form.add_error(
                    None,
                    "ایمیل یا رمز عبور اشتباه است."
                )

    else:

        form = LoginForm()

    return render(
        request,
        "accounts/login.html",
        {
            "form": form,
            "next": next_url,
        },
    )


def logout_view(request):

    auth_logout(request)

    messages.info(
        request,
        "شما از حساب کاربری خود خارج شدید."
    )

    return redirect("home")


@login_required
def dashboard(request):
    """
    داشبورد کاربر بعد از ورود/ثبت‌نام:
    خلاصه کیف پول و لینک‌های میان‌بر.
    """

    wallet, _ = Wallet.objects.get_or_create(
        user=request.user
    )

    recent_transactions = (
        wallet.transactions
        .order_by("-created_at")[:5]
    )

    return render(
        request,
        "accounts/dashboard.html",
        {
            "wallet": wallet,
            "transactions": recent_transactions,
        },
    )


@login_required
def wallet_detail(request):

    wallet, _ = Wallet.objects.get_or_create(
        user=request.user
    )

    form = WalletChargeForm()

    recent_transactions = (
        wallet.transactions
        .order_by("-created_at")[:10]
    )

    return render(
        request,
        "accounts/wallet_detail.html",
        {
            "wallet": wallet,
            "form": form,
            "transactions": recent_transactions,
        },
    )


@login_required
def wallet_charge(request):
    """
    شارژ کیف پول.

    شبیه‌سازی‌شده است: طبق تیکت درگاه پرداخت واقعی لازم نیست.
    با تایید فرم، مبلغ مستقیماً از طریق wallet.deposit()
    به موجودی اضافه می‌شود و یک WalletTransaction ثبت می‌گردد.
    """

    if request.method != "POST":
        return redirect("accounts:wallet_detail")

    form = WalletChargeForm(request.POST)

    if not form.is_valid():

        for field_errors in form.errors.values():

            for error in field_errors:
                messages.error(request, error)

        return redirect("accounts:wallet_detail")

    amount = form.cleaned_data["amount"]

    wallet, _ = Wallet.objects.get_or_create(
        user=request.user
    )

    wallet.deposit(
        amount,
        type="CHARGE",
        external_reference=(
            f"manual-charge-{request.user.pk}"
        ),
    )

    messages.success(
        request,
        "کیف پول با موفقیت شارژ شد."
    )

    return redirect("accounts:wallet_detail")


@login_required
def wallet_transactions(request):
    """
    تاریخچه کامل تراکنش‌های کیف پول،
    صفحه‌بندی‌شده و به ترتیب زمانی نزولی.
    """

    wallet, _ = Wallet.objects.get_or_create(
        user=request.user
    )

    transactions = (
        wallet.transactions
        .order_by("-created_at")
    )

    paginator = Paginator(
        transactions,
        TRANSACTIONS_PER_PAGE
    )

    page = paginator.get_page(
        request.GET.get("page")
    )

    return render(
        request,
        "accounts/wallet_transactions.html",
        {
            "wallet": wallet,
            "page_obj": page,
            "transactions": page.object_list,
        },
    )


def home(request):
    """
    صفحه اصلی سایت.

    برای کاربر لاگین‌کرده خلاصه‌ای از نوبت‌های آینده
    و لینک‌های سریع نشان می‌دهد.

    برای کاربر ناشناس یک صفحه معرفی ساده
    با دکمه ورود و ثبت‌نام است.
    """

    context = {}

    if request.user.is_authenticated:

        from appointments.models import Appointment

        upcoming = (
            Appointment.objects.filter(
                patient_user=request.user,
                status=Appointment.Status.RESERVED,
                visit_slot__start_at__gt=timezone.now(),
            )
            .select_related(
                "visit_slot__doctor__user"
            )
            .order_by(
                "visit_slot__start_at"
            )[:3]
        )

        context["upcoming_appointments"] = upcoming

    return render(
        request,
        "home.html",
        context,
    )