from django.contrib import admin
from .models import Specialty, Doctor, DoctorSpecialty, Review



@admin.register(Specialty)
class SpecialtyAdmin(admin.ModelAdmin):
    list_display = ('id','name','created_at')
    search_fields = ('name',)


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'verification_status', 'verified_at', 'created_at')
    list_filter = ('verification_status',)
    search_fields = ('user__email',)


@admin.register(DoctorSpecialty)
class DoctorSpecialtyAdmin(admin.ModelAdmin):
    list_display = ('id', 'doctor', 'specialty', 'created_at')


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'doctor', 'patient_user', 'rating', 'created_at')
    list_filter = ('rating',)
    search_fields = ('doctor__user__email', 'patient_user__email', 'comment')