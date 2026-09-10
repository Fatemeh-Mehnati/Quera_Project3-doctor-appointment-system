from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import redirect, render

from .forms import WalletChargeForm
from .models import Wallet

TRANSACTIONS_PER_PAGE = 20


# Create your views here.
def signup_view(request):
    return None


@login_required
def wallet_detail(request):
    """
    صفحه اصلی کیف پول: موجودی فعلی، فرم شارژ و ۱۰ تراکنش آخر.
    """
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