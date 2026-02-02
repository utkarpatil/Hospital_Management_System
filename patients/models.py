"""
Patient Profile and Medical History Models
"""
from django.db import models
from django.conf import settings

class PatientProfile(models.Model):
    """
    Detailed patient profile information
    """
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    )
    
    BLOOD_GROUP_CHOICES = (
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
        ('O+', 'O+'),
        ('O-', 'O-'),
    )
    
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='patient_profile'
    )
    
    # Personal Information
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUP_CHOICES, blank=True)
    height = models.DecimalField(max_digits=5, decimal_places=2, help_text="Height in cm", blank=True, null=True)
    weight = models.DecimalField(max_digits=5, decimal_places=2, help_text="Weight in kg", blank=True, null=True)
    
    # Contact Information
    address = models.TextField(blank=True)
    emergency_contact = models.CharField(max_length=15, blank=True)
    emergency_contact_name = models.CharField(max_length=100, blank=True)
    
    # Medical Background
    allergies = models.TextField(blank=True, help_text="List of known allergies")
    chronic_conditions = models.TextField(blank=True, help_text="Chronic diseases or conditions")
    current_medications = models.TextField(blank=True, help_text="Currently taking medications")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Profile: {self.user.get_full_name() or self.user.username}"
    
    class Meta:
        verbose_name = "Patient Profile"
        verbose_name_plural = "Patient Profiles"


class MedicalHistory(models.Model):
    """
    Timeline-based medical history entries
    """
    ENTRY_TYPE_CHOICES = (
        ('APPOINTMENT', 'Appointment'),
        ('PRESCRIPTION', 'Prescription'),
        ('LAB_REPORT', 'Lab Report'),
        ('DIAGNOSIS', 'Diagnosis'),
        ('PROCEDURE', 'Procedure'),
        ('NOTE', 'Medical Note'),
    )
    
    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='medical_history',
        limit_choices_to={'role': 'PATIENT'}
    )
    
    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='patient_histories',
        limit_choices_to={'role': 'DOCTOR'}
    )
    
    entry_type = models.CharField(max_length=20, choices=ENTRY_TYPE_CHOICES)
    title = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateTimeField()
    
    # Optional fields
    attachments = models.FileField(upload_to='medical_history/', blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.patient.username} - {self.entry_type} - {self.date.date()}"
    
    class Meta:
        verbose_name = "Medical History Entry"
        verbose_name_plural = "Medical History Entries"
        ordering = ['-date']