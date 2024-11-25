from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from .models import Doctor, Patient, PatientSymptom, Pharmacy, Referral, Symptom, ContactMessage, Appointment
from datetime import date,timedelta
from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist 
from django.conf import settings



def home(request):
    return render(request, 'home.html')

def new_appoint(request):
    return render(request, 'patient_dashboard.html')

def patient_profile(request):
    patient = request.user.patient  # Assuming the user is logged in and has a related Patient object
    return render(request, 'patient_profile.html', {'patient': patient})

def doctor_profile(request):
    doctor = request.user.doctor
    return render(request, 'doctor_profile.html', {'doctor': doctor})

def patient_dashboard(request):
    patient = request.user.patient
    symptoms = Symptom.objects.all()
    
    return render(request, 'patient_dashboard.html', {'patient': patient, 'symptoms': symptoms})

def contact_view(request):
    if request.method == 'POST':
        # Getting data from the form
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        contact_message = ContactMessage(
            name=name,
            email=email,
            subject=subject,
            message=message
        )
        contact_message.save()  
        return render(request, 'contact.html',{'message': 'Thanks for contacting us'})  # Redirect to a success page or show a success message

    return render(request, 'contact.html')

def doctor_register(request):
    if request.method == 'POST':
        # Collect form data
        name = request.POST['name']
        location = request.POST['location']
        pin = request.POST['pin']
        specialty = request.POST['specialty']
        phone_number = request.POST['phone_number']
        email = request.POST['email']
        password = request.POST['password']

        # Step 1: Create a User instance
        user = User.objects.create_user(username=email, password=password)
        user.save()
        
        # Step 2: Create the Doctor instance and associate it with the user
        doctor = Doctor.objects.create(
            name=name,
            location=location,
            specialty=specialty,
            phone_number=phone_number,
            email=email,
            pin_number=pin,
            user=user  # Assign the user to the doctor instance
        )

        # Step 3: Get selected symptoms from the form
        selected_symptoms = request.POST.getlist('symptoms')  # Get list of selected symptoms
        symptoms = Symptom.objects.filter(id__in=selected_symptoms)

        # Step 4: Link symptoms to the doctor (many-to-many relationship)
        doctor.symptoms.set(symptoms)

        # Step 5: Save the doctor instance
        doctor.save()

        # Redirect to a success page (e.g., doctor dashboard)
        return render(request, 'doctor_register.html', {'message': "Registration Successful"})
    
    # If not a POST request, fetch all symptoms for the form
    symptoms = Symptom.objects.all()
    return render(request, 'doctor_register.html', {'symptoms': symptoms})

def patient_register(request):
    if request.method == 'POST':
        name = request.POST['name']
        age = request.POST['age']
        location = request.POST['location']
        pin = request.POST['pin']
        phone_number = request.POST['phone_number']
        email = request.POST['email']
        
        # Create User object with email as the username
        user = User.objects.create_user(username=email, password=request.POST['password'])
        user.save()  # Save the User instance
        
        # Create Patient instance linked to the newly created user
        patient = Patient.objects.create(
            user=user,  # Associate this patient with the user
            name=name, 
            age=age, 
            location=location, 
            phone_number=phone_number, 
            email=email, 
            pin_number=pin
        )
        patient.save()  # Save the Patient instance

        # Return a response indicating successful registration
        return render(request, 'patient_register.html', {'message': "Registration successful"})
    
    return render(request, 'patient_register.html')

def doctor_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('doctor_dashboard')
        else:
            return render(request, 'doctor_login.html', {'error':'Check the Username or Password'})
        
    return render(request, 'doctor_login.html')

def patient_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('patient_dashboard')
        else:
            return render(request, 'patient_login.html', {"error":"Check the Username or Password"})
    return render(request, 'patient_login.html')


def refer_doctor_and_pharmacy(patient_id):
    patient = Patient.objects.get(id=patient_id)
    symptoms = PatientSymptom.objects.filter(patient=patient)

    # Find relevant doctors and pharmacies based on patient location
    relevant_doctors = Doctor.objects.filter(location=patient.location)
    relevant_pharmacies = Pharmacy.objects.filter(location=patient.location)

    if relevant_doctors and relevant_pharmacies:
        doctor = relevant_doctors.first()
        pharmacy = relevant_pharmacies.first()

        referral = Referral.objects.create(
            patient=patient,
            referred_doctor=doctor,
            referred_pharmacy=pharmacy
        )
        return referral
    return None


@login_required
def doctor_dashboard(request):
    try:
        # Get the logged-in doctor based on the user
        doctor = Doctor.objects.get(user=request.user)
    except Doctor.DoesNotExist:
        return render(request, 'doctor_dashboard.html', {'error_message': 'No doctor profile found for the logged-in user.'})

    appointment = Appointment.objects.filter(doctor=doctor)
    
    # Prepare context for the template
    context = {
        'doctor': doctor,
        'appointments': appointment
    }
    
    return render(request, 'doctor_dashboard.html', context)


@login_required
def appointment_view(request):
    patient = Patient.objects.get(user=request.user)
    symptoms = Symptom.objects.all()  # Fetch all symptoms
    relevant_doctors = None
    relevant_pharmacies = None
    selected_symptom = None
    today = date.today()

    future_dates = [today + timedelta(days=i) for i in range(1, 6)]
    # Check if the form was submitted and retrieve the symptom if it was
    if request.method == 'POST':
        # Get selected symptom from the POST data
        symptom_id = request.POST.get('symptom')
        print("symptomsssss", symptom_id)
        
        if symptom_id:
            selected_symptom = Symptom.objects.get(id=symptom_id)
        
        symptom_description = request.POST.get('symptom_description')

        # Logic for referring a doctor based on the symptom
        if 'refer_doctor' in request.POST and selected_symptom:
            relevant_doctors = Doctor.objects.filter(symptoms=selected_symptom)

        # Logic for referring a pharmacy based on the patient's pin code
        if 'refer_pharmacy' in request.POST and selected_symptom:
            relevant_pharmacies = Pharmacy.objects.filter(pin_number=patient.pin_number)

        # Handling appointment confirmation for doctor referral
        if 'confirm_appointment' in request.POST and selected_symptom:
            doctor_id = request.POST.get('selected_doctor')
            doctor = Doctor.objects.get(id=doctor_id)
            appointment_date = request.POST.get('appointment_date')

            print("appointment_date", appointment_date)

            try:
                # Ensure appointment date is in the correct format
                today = date.today()
                appointment_date = today+timedelta(days=1)
                
                if appointment_date < today:
                    raise ValueError("Appointment date cannot be in the past.")
            except ValueError as e:
                return render(request, 'appointment.html', {
                    'patient': patient,
                    'symptoms': symptoms,
                    'selected_symptom': selected_symptom,  # Retain the selected symptom
                    'relevant_doctors': relevant_doctors,
                    'relevant_pharmacies': relevant_pharmacies,
                    'today': today,
                    'error_message': str(e)
                })

            # Create the appointment
            appointment = Appointment.objects.create(
                patient=patient,
                doctor=doctor,
                symptom=Symptom.objects.get(id=symptom_id) if symptom_id else None,  # Assign the actual Symptom instance here
                symptom_description=symptom_description,
                appointment_date=appointment_date  # Save the appointment date
            )
            print("symptoms", selected_symptom);
            return redirect('appointment_success', appointment_id=appointment.id)

        # Handling appointment confirmation for pharmacy referral
        if 'confirm_pharmacy' in request.POST and selected_symptom:
            pharmacy_id = request.POST.get('selected_pharmacy')
            pharmacy = Pharmacy.objects.get(id=pharmacy_id)
            Referral.objects.create(
                patient=patient,
                referred_pharmacy=pharmacy,
                symptom=selected_symptom,
                symptom_description=symptom_description
            )
            return redirect('appointment_success')

    # If no POST request or the page is refreshed, ensure selected_symptom persists in the context
    return render(request, 'appointment.html', {
        'patient': patient,
        'symptoms': symptoms,
        'selected_symptom': selected_symptom,  # Persist the selected symptom in the context
        'relevant_doctors': relevant_doctors,
        'relevant_pharmacies': relevant_pharmacies,
        'today': today,
    })

@login_required
def appointment_success(request, appointment_id):
    # Fetch the appointment from the database
    appointment = Appointment.objects.get(id=appointment_id)
    print("Appointment_id", appointment.doctor)
    return render(request, 'appointment_success.html', {
        'patient': appointment.patient,
        'doctor': appointment.doctor,
        'symptom': appointment.symptom,
        'symptom_description': appointment.symptom_description,
        'appointment_date': appointment.appointment_date
    })


