# Create your views here.
from django.core.paginator import Paginator
from django.db.models import Prefetch, Q
from django.shortcuts import get_object_or_404, render
from django.utils import timezone

from appointments.models import TimeSlot

from .forms import DoctorSearchForm
from .models import Doctor


DOCTORS_PER_PAGE = 12


def _approved_doctors():
    """
    کوئری پایه پزشکان تاییدشده.

    select_related روی user می‌زنیم چون نام پزشک از مدل کاربر می‌آید و
    بدون آن برای هر پزشک یک کوئری جداگانه اجرا می‌شود.
    prefetch_related تخصص‌ها را در یک کوئری اضافه می‌آورد.
    """
    return (
        Doctor.objects.filter(verification_status=Doctor.VerificationStatus.APPROVED)
        .select_related("user")
        .prefetch_related("doctor_specialties__specialty")
    )


def doctor_list(request):
    """
    لیست پزشکان همراه با جستجو، فیلتر تخصص و صفحه‌بندی.

    جستجو روی نام و نام خانوادگی پزشک و همچنین نام تخصص انجام می‌شود.
    جستجوی خالی همه پزشکان را برمی‌گرداند.
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
            doctors = doctors.filter(doctor_specialties__specialty=specialty)

    # فیلتر روی رابطه چندبه‌چند می‌تواند یک پزشک را چند بار برگرداند
    doctors = doctors.distinct().order_by("user__last_name", "user__first_name")

    paginator = Paginator(doctors, DOCTORS_PER_PAGE)
    page = paginator.get_page(request.GET.get("page"))

    # برای حفظ پارامترهای جستجو هنگام رفتن به صفحه بعد
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
    صفحه جزئیات یک پزشک به همراه بازه‌های زمانی قابل رزرو.

    بازه قابل رزرو یعنی: فعال باشد، هنوز نوبتی به آن وصل نشده باشد،
    و زمان شروعش در آینده باشد.
    """
    available_slots = (
        TimeSlot.objects.filter(
            is_active=True,
            appointment__isnull=True,
            start_at__gt=timezone.now(),
        )
        .prefetch_related("price_history")
        .order_by("start_at")
    )

    doctor = get_object_or_404(
        _approved_doctors().prefetch_related(
            Prefetch("time_slots", queryset=available_slots, to_attr="available_slots")
        ),
        pk=pk,
    )

    # قیمت هر بازه از آخرین رکورد تاریخچه خوانده می‌شود.
    # ordering مدل SlotPriceHistory روی effective_at نزولی است،
    # پس اولین رکورد همان قیمت فعلی است.
    slots = []
    for slot in doctor.available_slots:
        latest_price = slot.price_history.all().first()
        slots.append(
            {
                "slot": slot,
                "price": latest_price.amount if latest_price else None,
            }
        )

    specialties = [ds.specialty for ds in doctor.doctor_specialties.all()]

    return render(
        request,
        "doctors/doctor_detail.html",
        {
            "doctor": doctor,
            "specialties": specialties,
            "slots": slots,
        },
    )