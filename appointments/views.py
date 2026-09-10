from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from accounts.models import InsufficientBalanceError, Wallet

from .models import Appointment, TimeSlot


def _current_price(slot):
    """
    قیمت فعلی یک بازه زمانی.

    قیمت روی خود TimeSlot ذخیره نمی‌شود و از آخرین رکورد تاریخچه خوانده
    می‌شود. ordering مدل SlotPriceHistory نزولی روی effective_at است،
    پس اولین رکورد همان قیمت فعلی است. اگر ادمین برای بازه قیمتی ثبت
    نکرده باشد None برمی‌گردد.
    """
    latest = slot.price_history.all().first()
    return latest.amount if latest else None


@login_required
def available_slots(request, doctor_id):
    """بازه‌های زمانی قابل رزرو یک پزشک."""
    slots = (
        TimeSlot.objects.filter(
            doctor_id=doctor_id,
            is_active=True,
            appointment__isnull=True,
            start_at__gt=timezone.now(),
        )
        .select_related("doctor__user")
        .prefetch_related("price_history")
        .order_by("start_at")
    )

    items = [{"slot": slot, "price": _current_price(slot)} for slot in slots]

    return render(
        request,
        "appointments/available_slots.html",
        {"doctor_id": doctor_id, "items": items},
    )


@login_required
@transaction.atomic
def reserve_appointment(request, slot_id):
    """
    رزرو یک بازه زمانی و کسر هزینه از کیف پول.

    کل عملیات داخل یک تراکنش اتمیک است: اگر هر مرحله شکست بخورد،
    نه پولی کسر می‌شود و نه نوبتی ثبت. select_for_update ردیف بازه را
    قفل می‌کند تا دو کاربر هم‌زمان نتوانند یک بازه را بگیرند.
    """
    if request.method != "POST":
        return redirect("doctors:doctor_list")

    slot = get_object_or_404(
        TimeSlot.objects.select_for_update().select_related("doctor"),
        pk=slot_id,
    )
    doctor_url = redirect("doctors:doctor_detail", pk=slot.doctor_id)

    if not slot.is_active:
        messages.error(request, "این بازه زمانی در دسترس نیست.")
        return doctor_url

    if slot.start_at <= timezone.now():
        messages.error(request, "زمان این بازه گذشته است.")
        return doctor_url

    if hasattr(slot, "appointment"):
        messages.error(request, "این بازه قبلاً رزرو شده است.")
        return doctor_url

    price = _current_price(slot)
    if price is None:
        messages.error(request, "برای این بازه هزینه‌ای تعیین نشده است.")
        return doctor_url

    # withdraw خودش ردیف کیف پول را قفل می‌کند و اگر موجودی کافی
    # نباشد InsufficientBalanceError raise می‌کند؛ در آن صورت هیچ
    # چیزی تغییر نمی‌کند (چون داخل transaction.atomic اجرا می‌شود).
    try:
        wallet = Wallet.objects.get(user=request.user)
    except Wallet.DoesNotExist:
        messages.error(request, "کیف پولی برای حساب شما یافت نشد.")
        return doctor_url

    try:
        wallet.withdraw(
            price,
            type="APPOINTMENT",
            external_reference=f"slot:{slot.pk}",
        )
    except InsufficientBalanceError:
        messages.error(
            request,
            "موجودی کیف پول شما کافی نیست. لطفاً ابتدا کیف پول را شارژ کنید.",
        )
        return doctor_url

    appointment = Appointment.objects.create(
        patient_user=request.user,
        visit_slot=slot,
        reserved_price=price,
        status=Appointment.Status.RESERVED,
    )

    # ایمیل بعد از commit موفق ارسال می‌شود، نه وسط تراکنش —
    # وگرنه اگر تراکنش rollback شود کاربر ایمیل تاییدیه‌ای می‌گیرد
    # برای نوبتی که ثبت نشده است.
    transaction.on_commit(lambda: _send_confirmation(appointment))

    messages.success(request, "نوبت شما با موفقیت رزرو شد.")
    return redirect("appointments:my_appointments")


def _send_confirmation(appointment):
    doctor_name = appointment.visit_slot.doctor.user.get_full_name()
    when = appointment.visit_slot.start_at.strftime("%Y-%m-%d %H:%M")

    send_mail(
        subject="تاییدیه رزرو نوبت",
        message=(
            f"نوبت شما با موفقیت ثبت شد.\n\n"
            f"پزشک: {doctor_name}\n"
            f"زمان: {when}\n"
            f"مبلغ پرداختی: {appointment.reserved_price}\n\n"
            f"کد پیگیری: {appointment.pk}"
        ),
        from_email=None,
        recipient_list=[appointment.patient_user.email],
        fail_silently=True,
    )


@login_required
def my_appointments(request):
    """نوبت‌های کاربر جاری."""
    appointments = (
        Appointment.objects.filter(patient_user=request.user)
        .select_related("visit_slot__doctor__user")
        .order_by("-created_at")
    )
    return render(
        request,
        "appointments/my_appointments.html",
        {"appointments": appointments, "now": timezone.now()},
    )


@login_required
@transaction.atomic
def cancel_appointment(request, pk):
    """
    لغو نوبت و بازگشت وجه به کیف پول.

    فقط نوبت‌هایی که هنوز در وضعیت RESERVED هستند و زمانشان نرسیده
    قابل لغو هستند.
    """
    if request.method != "POST":
        return redirect("appointments:my_appointments")

    appointment = get_object_or_404(
        Appointment.objects.select_for_update().select_related("visit_slot"),
        pk=pk,
        patient_user=request.user,
    )

    if appointment.status != Appointment.Status.RESERVED:
        messages.error(request, "این نوبت قابل لغو نیست.")
        return redirect("appointments:my_appointments")

    if appointment.visit_slot.start_at <= timezone.now():
        messages.error(request, "زمان این نوبت گذشته است و قابل لغو نیست.")
        return redirect("appointments:my_appointments")

    wallet = Wallet.objects.get(user=request.user)
    wallet.deposit(
        appointment.reserved_price,
        type="REFUND",
        external_reference=f"refund:{appointment.pk}",
    )

    appointment.status = Appointment.Status.CANCELLED
    appointment.cancelled_by_user = request.user
    appointment.cancelled_at = timezone.now()
    appointment.save(
        update_fields=["status", "cancelled_by_user", "cancelled_at", "updated_at"]
    )

    messages.success(request, "نوبت لغو شد و مبلغ به کیف پول شما بازگشت.")
    return redirect("appointments:my_appointments")