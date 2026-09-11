from django.urls import path

from . import views

app_name = "appointments"

urlpatterns = [
    path("doctor/<int:doctor_id>/slots/", views.available_slots, name="available_slots"),
    path("reserve/<int:slot_id>/", views.reserve_appointment, name="reserve"),
    path("my/", views.my_appointments, name="my_appointments"),
    path("<int:pk>/cancel/", views.cancel_appointment, name="cancel"),
]