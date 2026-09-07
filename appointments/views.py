from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.core.mail import send_mail

from .models import Appointment, TimeSlot, SlotPriceHistory
from accounts.models import Wallet, WalletTransaction

@login_required
def available_slots(request, doctor_id):
    slots = TimeSlot.objects.filter(
        doctor_id=doctor_id,
        is_active=True,
        appointment__isnull=True,
    )

    return render(
        request,
        "appointments/available_slots.html",
        {
            "slots": slots,
        },
    )

@login_required
@transaction.atomic
def reserve_appointment(request, slot_id):

    if request.method != "POST":
        return redirect("appointments:available_slots")

    slot = (
        TimeSlot.objects
        .select_for_update()
        .select_related("doctor")
        .get(id=slot_id)
    )

    # reserved error
    if hasattr(slot, "appointment"):
        messages.error(request, "This slot is already reserved.")
        return redirect(...)

    # add price
    price = ...

    # find wallet
    wallet = ...

    # balance check
    if wallet.balance < price:
        messages.error(
            request,
            "Insufficient wallet balance."
        )
        return redirect(...)

    # transaction
    wallet.balance -= price
    wallet.save()

    # add Appointment
    appointment = Appointment.objects.create(
        patient_user=request.user,
        visit_slot=slot,
        reserved_price=price,
        status=...,
    )

    # save appoinments
    WalletTransaction.objects.create(
        ...
    )

    # Email
    send_mail(
        subject="Appointment confirmation",
        message="Your appointment has been confirmed.",
        from_email=None,
        recipient_list=[request.user.email],
    )

    messages.success(
        request,
        "Appointment reserved successfully."
    )

    return redirect(...)