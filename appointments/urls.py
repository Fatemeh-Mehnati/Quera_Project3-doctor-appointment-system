from django.urls import path
import views

urlpatterns = [
    path('appoinments/', views.appoinment, name='appoinments'),
]

app_name = 'appointments'