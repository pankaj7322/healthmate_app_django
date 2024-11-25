from django.db import models
from django.contrib.auth.models import User

class Symptom(models.Model):
    symptom_name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.symptom_name

class Doctor(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    specialty = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    email = models.EmailField()
    pin_number = models.CharField(max_length=6, null=True, blank=True)
    symptoms = models.ManyToManyField(Symptom, related_name="doctors", blank=True)  # Added Many-to-Many relationship  # Make pin_number nullable
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # Add this line

    def __str__(self):
        return self.name

class Patient(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    age = models.IntegerField()
    location = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    email = models.EmailField()
    pin_number = models.CharField(max_length=6, null=True, blank=True)  # Make pin_number nullable

    def __str__(self):
        return self.name

class Pharmacy(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    contact_number = models.CharField(max_length=15)
    email = models.EmailField()
    pin_number = models.CharField(max_length=6, null=True, blank=True)  # Make pin_number nullable

    def __str__(self):
        return self.name

class PatientSymptom(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    symptom = models.ForeignKey(Symptom, on_delete=models.CASCADE)
    date_reported = models.DateTimeField(auto_now_add=True)

class Referral(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    referred_doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    referred_pharmacy = models.ForeignKey(Pharmacy, null=True, blank=True, on_delete=models.SET_NULL)
    date_referred = models.DateTimeField(auto_now_add=True)
    symptom = models.ForeignKey(Symptom, on_delete=models.CASCADE)
    symptom_description = models.TextField(blank=True, null=True) 
    doctor_location = models.CharField(max_length=255, blank=True, null=True)  # New field for doctor's location

    def save(self, *args, **kwargs):
        # Automatically set doctor_location when saving the referral
        self.doctor_location = self.referred_doctor.location
        super().save(*args, **kwargs)
        
    def __str__(self):
         return f"Referral for {self.patient.name} to {self.referred_doctor.name} at {self.date_referred}"
    

class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=100)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.name} about {self.subject}"
    

class Appointment(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    symptom = models.ForeignKey(Symptom, on_delete=models.SET_NULL, null=True, blank=True)
    symptom_description = models.TextField()
    appointment_date = models.DateField()
    status = models.CharField(max_length=50, default="Scheduled")  # Add a status like "Scheduled", "Confirmed", etc.

    def __str__(self):
        return f"Appointment for {self.patient.name} with Dr. {self.doctor.name} on {self.appointment_date}"
    

