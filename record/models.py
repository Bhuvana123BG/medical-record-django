
from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    mobile_number = models.CharField(max_length=15, blank=True)
class Doctor(models.Model):
    name = models.CharField(max_length=100)
    specialty = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.name 

class MedicalRecord(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True)
    date_of_visit = models.DateField()
    purpose = models.TextField() 
    prescription_url = models.URLField(max_length=500, blank=True, null=True)

    summary = models.TextField(blank=True, null=True) 
    


    def __str__(self):
        return f"Record of {self.user.username} on {self.date_of_visit}"


