"""
Custom User Model for Healthcare System
Supports both Doctor and Patient roles
"""
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """
    Custom User model with role-based access
    """
    ROLE_CHOICES = (
        ('DOCTOR', 'Doctor'),
        ('PATIENT', 'Patient'),
    )
    
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    phone = models.CharField(max_length=15, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.username} - {self.role}"
    
    @property
    def is_doctor(self):
        return self.role == 'DOCTOR'
    
    @property
    def is_patient(self):
        return self.role == 'PATIENT'