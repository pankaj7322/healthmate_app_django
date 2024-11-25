from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name = 'home'),
    path('doctor/register/', views.doctor_register, name='doctor_register'),
    path('patient/register/', views.patient_register, name='patient_register'),
    path('doctor/login/', views.doctor_login, name='doctor_login'),
    path('patient/login/', views.patient_login, name='patient_login'),
    path('doctor/dashboard/', views.doctor_dashboard, name='doctor_dashboard'),
    path('patient/dashboard/', views.patient_dashboard, name='patient_dashboard'),  
    path('refer/<int:patient_id>/', views.refer_doctor_and_pharmacy, name='refer'),
    path("new_appointment", views.new_appoint, name = "new_appointment"),
    path('patient_profile/', views.patient_profile, name='patient_profile'),
    path('book_appointment/', views.appointment_view, name = "book_appointment"),
    path('contact', views.contact_view, name = "contact"),
    path('appointment_success/<int:appointment_id>/', views.appointment_success, name='appointment_success'),
    path('doctor/profile/', views.doctor_profile, name='doctor_profile'),    

]
