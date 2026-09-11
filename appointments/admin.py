from django.contrib import admin
from .models import Appointment , TimeSlot


@admin.register(TimeSlot)
class TimeSlot(admin.ModelAdmin):
    list_display = (
        'id',
        'doctor',
        'start_at',
        'end_at',
        'is_active',
        'created_at',
    )
    list_filter = ('is_active',)
    search_fields = ('doctor__user__email',)


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'patient_user',
        'visit_slot',
        'reserved_price',
        'status',
        'created_at',
    )
    list_filter = ('status',)
    search_fields = ('patient_user__email',)