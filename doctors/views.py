# Create your views here.
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Avg, OuterRef, Prefetch, Q, Subquery
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from appointments.models import Appointment, TimeSlot

from .forms import DoctorReviewForm, DoctorSearchForm
from .models import Doctor, Review


DOCTORS_PER_PAGE = 12


def _approved_doctors():
    """
    کوئری پایه پزشکان تاییدشده.
    """
    avg_rating_subquery = (
        Review.objects.filter(doctor=OuterRef("pk"))
        .values("doctor")
        .annotate(avg=Avg("rating"))
        .values("avg")
    )

    return (
        Doctor.objects.filter(
            verification_status=Doctor.VerificationStatus.APPROVED
        )
        .select_related("user")
        .prefetch_related("doctor_specialties__specialty")
        .annotate(avg_rating=Subquery(avg_rating_subquery))
    )


def doctor_list(request):
    """
    لیست پزشکان همراه با جستجو، فیلتر تخصص و صفحه‌بندی.
    """
    form = DoctorSearchForm(request.GET or None)
    doctors = _approved_doctors()

    if form.is_valid():
        query = form.cleaned_data.get("query")
        specialty = form.cleaned_data.get("specialty")

        if query:
            doctors = doctors.filter(
                Q(user__first_name__icontains=query)
                | Q(user__last_name__icontains=query)
                | Q(doctor_specialties__specialty__name__icontains=query)
            )

        if specialty:
            doctors = doctors.filter(
                doctor_specialties__specialty=specialty
            )

    doctors = doctors.distinct().order_by(
        "user__last_name",
        "user__first_name",
    )

    paginator = Paginator(doctors, DOCTORS_PER_PAGE)
    page = paginator.get_page(request.GET.get("page"))

    params = request.GET.copy()
    params.pop("page", None)

    return render(
        request,
        "doctors/doctor_list.html",
        {
            "form": form,
            "page_obj": page,
            "doctors": page.object_list,
            "total_count": paginator.count,
            "querystring": params.urlencode(),
        },
    )


def doctor_detail(request, pk):
    """
    صفحه جزئیات پزشک به همراه بازه‌های زمانی قابل رزرو.

    یک TimeSlot زمانی قابل رزرو است اگر:
    - فعال باشد
    - زمان آن در آینده باشد
    - Appointment با وضعیت RESERVED یا COMPLETED نداشته باشد

    بنابراین اگر Appointment قبلی CANCELLED شده باشد،
    TimeSlot دوباره قابل رزرو خواهد بود.
    """

    available_slots = (
        TimeSlot.objects.filter(
            doctor_id=pk,
            is_active=True,
            start_at__gt=timezone.now(),
        )
        .exclude(
            appointments__status__in=[
                Appointment.Status.RESERVED,
                Appointment.Status.COMPLETED,
            ]
        )
        .prefetch_related("price_history")
        .order_by("start_at")
    )

    doctor = get_object_or_404(
        _approved_doctors().prefetch_related(
            Prefetch(
                "time_slots",
                queryset=available_slots,
                to_attr="available_slots",
            )
        ),
        pk=pk,
    )

    # قیمت فعلی هر TimeSlot
    slots = []

    for slot in doctor.available_slots:
        latest_price = slot.price_history.all().first()

        slots.append(
            {
                "slot": slot,
                "price": latest_price.amount if latest_price else None,
            }
        )

    specialties = [
        ds.specialty
        for ds in doctor.doctor_specialties.all()
    ]

    # نظرات پزشک
    reviews = (
        doctor.reviews
        .select_related("patient_user")
        .order_by("-created_at")
    )

    reviews_count = reviews.count()

    can_review = False
    existing_review = None

    if request.user.is_authenticated:

        # کاربر باید حداقل یک ویزیت COMPLETED داشته باشد.
        can_review = Appointment.objects.filter(
            patient_user=request.user,
            visit_slot__doctor=doctor,
            status=Appointment.Status.COMPLETED,
        ).exists()

        # بررسی اینکه کاربر قبلاً برای این پزشک نظر ثبت کرده یا نه.
        existing_review = Review.objects.filter(
            doctor=doctor,
            patient_user=request.user,
        ).first()

        # اگر قبلاً نظر ثبت شده باشد، دیگر اجازه ثبت نظر جدید ندارد.
        if existing_review:
            can_review = False

    review_form = DoctorReviewForm()

    return render(
        request,
        "doctors/doctor_detail.html",
        {
            "doctor": doctor,
            "specialties": specialties,
            "slots": slots,
            "reviews": reviews,
            "reviews_count": reviews_count,
            "can_review": can_review,
            "existing_review": existing_review,
            "review_form": review_form,
        },
    )


@login_required
def submit_review(request, pk):
    """
    ثبت نظر بیمار برای پزشک.

    شرایط ثبت نظر:
    - کاربر باید حداقل یک ویزیت COMPLETED با پزشک داشته باشد.
    - هر کاربر فقط یک بار می‌تواند برای هر پزشک نظر ثبت کند.
    - اگر قبلاً نظر ثبت شده باشد، نظر جدید رد می‌شود.
    - نظر قبلی قابل ویرایش یا جایگزینی نیست.
    """

    doctor = get_object_or_404(
        _approved_doctors(),
        pk=pk,
    )

    doctor_url = redirect(
        "doctors:doctor_detail",
        pk=doctor.pk,
    )

    if request.method != "POST":
        return doctor_url

    # بررسی اینکه کاربر واقعاً این پزشک را ویزیت کرده است.
    has_completed_visit = Appointment.objects.filter(
        patient_user=request.user,
        visit_slot__doctor=doctor,
        status=Appointment.Status.COMPLETED,
    ).exists()

    if not has_completed_visit:
        messages.error(
            request,
            "فقط بیمارانی که این پزشک را ویزیت کرده‌اند "
            "می‌توانند نظر ثبت کنند.",
        )
        return doctor_url

    # جلوگیری از ثبت نظر تکراری
    existing_review = Review.objects.filter(
        doctor=doctor,
        patient_user=request.user,
    ).exists()

    if existing_review:
        messages.error(
            request,
            "شما قبلاً برای این پزشک نظر ثبت کرده‌اید و امکان ثبت نظر مجدد ندارید.",
        )
        return doctor_url

    form = DoctorReviewForm(request.POST)

    if not form.is_valid():
        for field_errors in form.errors.values():
            for error in field_errors:
                messages.error(request, error)

        return doctor_url

    # فقط ایجاد نظر جدید؛ هیچ update ای انجام نمی‌شود.
    Review.objects.create(
        doctor=doctor,
        patient_user=request.user,
        rating=form.cleaned_data["rating"],
        comment=form.cleaned_data["comment"],
    )

    messages.success(
        request,
        "نظر شما با موفقیت ثبت شد.",
    )

    return doctor_url