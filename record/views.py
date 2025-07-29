from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from django.db.models import Prefetch
from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.core.exceptions import ValidationError


from .models import CustomUser, MedicalRecord, Doctor
from django.db import IntegrityError
from .summarizer import summarize_prescription
import tempfile
import csv
import os
from django.conf import settings 
from .utils import upload_to_supabase
from datetime import datetime
from django.utils import timezone
def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        mobile_number=request.POST.get('mobile_number','').strip()
        if not username or not email or not password1 or not password2:
            messages.error(request, "All fields are required.")
            return render(request, 'record/register.html')

        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return render(request, 'record/register.html')

        try:
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password1
            )
            user.mobile_number = mobile_number 
            user.save()
            messages.success(request, "Registration successful. Please log in.")
            return redirect('login')
        except IntegrityError:
            messages.error(request, "Username already exists.")
            return render(request, 'record/register.html')

    return render(request, 'record/register.html')

def login_view(request):
    if request.method == "POST":
        username = request.POST.get('username').strip()
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('record_list')
        else:
            messages.error(request, "Invalid username or password.")
            return redirect('login')
    return render(request, 'record/login.html')


@login_required
def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def profile_view(request):
    return render(request, 'record/profile.html', {'user': request.user})

@login_required
def record_list(request):
    query = request.GET.get('q', '')
    doctor_filter = request.GET.get('doctor', '')

    records = MedicalRecord.objects.select_related('doctor').filter(user=request.user)

    if query:
        records = records.filter(purpose__icontains=query)

    if doctor_filter:
        records = records.filter(doctor__id=doctor_filter)

    doctors = Doctor.objects.all()

    paginator = Paginator(records.order_by('-date_of_visit'), 5)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'record/record_list.html', {
        'page_obj': page_obj,
        'query': query,
        'doctor_filter': doctor_filter,
        'doctors': doctors,
    })




@login_required
def add_record(request):
    doctors = Doctor.objects.all()

    if request.method == 'POST':
        doctor_id = request.POST.get('doctor')
        new_doctor_name = request.POST.get('new_doctor_name', '').strip()
        new_doctor_specialty = request.POST.get('new_doctor_specialty', '').strip()
        date_of_visit = request.POST.get('date_of_visit')
        purpose = request.POST.get('purpose').strip()
        prescription = request.FILES.get('prescription')

        if new_doctor_name:
            doctor, created = Doctor.objects.get_or_create(
                name=new_doctor_name,
                defaults={'specialty': new_doctor_specialty}
            )
        else:
            doctor = get_object_or_404(Doctor, id=doctor_id)

        duplicate = MedicalRecord.objects.filter(
            user=request.user,
            doctor=doctor,
            date_of_visit=date_of_visit,
            purpose__iexact=purpose
        ).exists()

        if duplicate:
            messages.error(request, 'Record already exists.')
            return render(request, 'record/add_record.html', {
                'doctors': doctors,
                'doctor_selected': doctor.id,
                'date_of_visit': date_of_visit,
                'purpose': purpose
            })

        summary = ""
        signed_url = None

        if prescription:
            import tempfile
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                for chunk in prescription.chunks():
                    tmp.write(chunk)
                tmp_path = tmp.name

            
            summary = summarize_prescription(tmp_path)

         
         
            filename = f"{request.user.username}_{timezone.now().strftime('%Y%m%d%H%M%S')}_prescription.pdf"
            with open(tmp_path, "rb") as file:
                signed_url = upload_to_supabase(file, filename)
        else:
            signed_url = None
        MedicalRecord.objects.create(
            user=request.user,
            doctor=doctor,
            date_of_visit=date_of_visit,
            purpose=purpose,
            prescription_url=signed_url,
            summary=summary
        )


        messages.success(request, 'Record added successfully.')
        return redirect('record_list')

    return render(request, 'record/add_record.html', {'doctors': doctors})
@login_required
def edit_record(request, record_id):
    record = get_object_or_404(MedicalRecord, id=record_id)
    doctors = Doctor.objects.all()

    if request.method == 'POST':
        
        doctor_id = request.POST.get('doctor')
        date_of_visit = request.POST.get('date_of_visit')
        purpose = request.POST.get('purpose')
        prescription_file = request.FILES.get('prescription')  

        
        errors = []
        if not doctor_id:
            errors.append("Doctor must be selected.")
        if not date_of_visit:
            errors.append("Date of Visit is required.")
        if not purpose or purpose.strip() == "":
            errors.append("Purpose is required.")

    
        try:
            doctor = Doctor.objects.get(id=doctor_id)
        except Doctor.DoesNotExist:
            errors.append("Selected doctor does not exist.")

       
        if errors:
            return render(request, 'record/edit_record.html', {
                'record': record,
                'doctors': doctors,
                'errors': errors, 
                'form_data': {
                    'doctor_id': doctor_id,
                    'date_of_visit': date_of_visit,
                    'purpose': purpose,
                }
            })

        try:
            record.doctor = doctor
            record.date_of_visit = date_of_visit
            record.purpose = purpose

            if prescription_file:
                record.prescription = prescription_file


                from .summarizer import summarize_prescription
                record.save()  
                record.summary = summarize_prescription(record.prescription.path)

            record.save()
            messages.success(request, "Medical record updated successfully.")
            return redirect('record_list')

        except ValidationError as ve:
            errors = ve.messages
            return render(request, 'record/edit_record.html', {
                'record': record,
                'doctors': doctors,
                'errors': errors,
                'form_data': {
                    'doctor_id': doctor_id,
                    'date_of_visit': date_of_visit,
                    'purpose': purpose,
                }
            })

    else:
        return render(request, 'record/edit_record.html', {
            'record': record,
            'doctors': doctors,
            'form_data': {
                'doctor_id': record.doctor.id,
                'date_of_visit': record.date_of_visit.strftime('%Y-%m-%d'),
                'purpose': record.purpose,
            }
        })


@login_required
def delete_record(request, record_id):
    record = get_object_or_404(MedicalRecord, id=record_id, user=request.user)

    if request.method == 'POST':
        record.delete()
        messages.success(request, 'Medical record deleted successfully.')
        return redirect('record_list')

    return render(request, 'record/delete_record.html', {'record': record})

@login_required
def grouped_records(request):
    
    user_records = MedicalRecord.objects.filter(user=request.user).order_by('-date_of_visit')

    doctors = Doctor.objects.filter(
        medicalrecord__user=request.user
    ).distinct().prefetch_related(
        Prefetch('medicalrecord_set', queryset=user_records, to_attr='user_records')
    )
    
    return render(request, 'record/grouped_records.html', {'doctors': doctors})

def predict_disease_view(request):
    result = None

    if request.method == "POST":
        symptoms = request.POST.get('symptoms', '').strip().lower()
        user_symptoms = set(sym.strip() for sym in symptoms.split(','))

        csv_path = os.path.join(settings.BASE_DIR, 'static', 'data', 'symptom_disease.csv')
        with open(csv_path, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                csv_symptoms = set(sym.strip().lower() for sym in row['symptoms'].split(','))
                if user_symptoms & csv_symptoms: 
                    result = {
                        'disease': row['disease'],
                        'medications': row['medications']
                    }
                    break
        if not result:
            result = {
                'disease': 'Unknown',
                'medications': 'Not available'
            }

    return render(request, 'record/predict_disease.html', {'result': result})

def about_view(request):
    return render(request, 'record/about.html')



   