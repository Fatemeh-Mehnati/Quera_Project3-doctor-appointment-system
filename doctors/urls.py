from django.urls import path

from . import views

app_name = "doctors"

urlpatterns = [
    path("", views.doctor_list, name="doctor_list"),
    path("<int:pk>/", views.doctor_detail, name="doctor_detail"),
    path("<int:pk>/review/", views.submit_review, name="submit_review"),
]