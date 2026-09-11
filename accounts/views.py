from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import redirect, render

from .forms import LoginForm, UserRegistrationForm, WalletChargeForm
from .models import Wallet

TRANSACTIONS_PER_PAGE = 20


def signup_view(request):

    if request.user.is_authenticated:
        return redirect("accounts:dashboard")

    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            messages.success(request, "ثبت‌نام شما با موفقیت انجام شد. خوش آمدید!")
            return redirect("accounts:dashboard")
    else:
        form = UserRegistrationForm()

    return render(request, "accounts/signup.html", {"form": form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect("accounts:dashboard")

    next_url = request.GET.get("next") or request.POST.get("next")

    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            user = authenticate(request, username=email, password=password)
            if user is not None:
                auth_login(request, user)
                return redirect(next_url or "accounts:dashboard")
            form.add_error(None, "ایمیل یا رمز عبور اشتباه است.")
    else:
        form = LoginForm()

    return render(request, "accounts/login.html", {"form": form, "next": next_url})


def logout_view(request):
    auth_logout(request)
    messages.info(request, "شما از حساب کاربری خود خارج شدید.")
    return redirect("home")


@login_required
def dashboard(request):
    """
    داشبورد کاربر بعد از ورود/ثبت‌نام: خلاصه کیف پول و لینک‌های میان‌بر.
    """
    wallet, _ = Wallet.objects.get_or_create(user=request.user)
    recent_transactions = wallet.transactions.order_by("-created_at")[:5]

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

    wallet, _ = Wallet.objects.get_or_create(user=request.user)
    form = WalletChargeForm()
    recent_transactions = wallet.transactions.order_by("-created_at")[:10]

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

    شبیه‌سازی‌شده است: طبق تیکت درگاه پرداخت واقعی لازم نیست. با تایید
    فرم، مبلغ مستقیماً از طریق wallet.deposit() به موجودی اضافه
    می‌شود و یک WalletTransaction ثبت می‌گردد.
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
    wallet, _ = Wallet.objects.get_or_create(user=request.user)
    wallet.deposit(
        amount,
        type="CHARGE",
        external_reference=f"manual-charge-{request.user.pk}",
    )

    messages.success(request, "کیف پول با موفقیت شارژ شد.")
    return redirect("accounts:wallet_detail")


@login_required
def wallet_transactions(request):
    """
    تاریخچه کامل تراکنش‌های کیف پول، صفحه‌بندی‌شده و به ترتیب زمانی نزولی.
    """
    wallet, _ = Wallet.objects.get_or_create(user=request.user)
    transactions = wallet.transactions.order_by("-created_at")

    paginator = Paginator(transactions, TRANSACTIONS_PER_PAGE)
    page = paginator.get_page(request.GET.get("page"))

    return render(
        request,
        "accounts/wallet_transactions.html",
        {
            "wallet": wallet,
            "page_obj": page,
            "transactions": page.object_list,
        },
    )