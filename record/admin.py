from django.contrib import admin
from .models import CustomUser,Doctor,MedicalRecord

# Register your models here.
admin.site.register(CustomUser)
admin.site.register(Doctor)
admin.site.register(MedicalRecord)