from django.urls import path

from . import views

app_name = "doctors"

urlpatterns = [
    path("", views.doctor_list, name="doctor_list"),
    path("<int:pk>/", views.doctor_detail, name="doctor_detail"),
]