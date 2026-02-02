"""
Doctor Profile and Patient Assignment Models
"""
from django.db import models
from django.conf import settings

class DoctorProfile(models.Model):
    """
    Detailed doctor profile information
    """
    SPECIALIZATION_CHOICES = (
        ('GENERAL', 'General Physician'),
        ('CARDIOLOGY', 'Cardiology'),
        ('NEUROLOGY', 'Neurology'),
        ('ORTHOPEDICS', 'Orthopedics'),
        ('PEDIATRICS', 'Pediatrics'),
        ('DERMATOLOGY', 'Dermatology'),
        ('PSYCHIATRY', 'Psychiatry'),
        ('GYNECOLOGY', 'Gynecology'),
        ('ENT', 'ENT'),
        ('OPHTHALMOLOGY', 'Ophthalmology'),
    )
    
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='doctor_profile'
    )
    
    # Professional Information
    specialization = models.CharField(max_length=50, choices=SPECIALIZATION_CHOICES)
    license_number = models.CharField(max_length=50, unique=True)
    qualification = models.CharField(max_length=200)
    experience_years = models.PositiveIntegerField(default=0)
    
    # Contact Information
    office_address = models.TextField(blank=True)
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Availability
    available_days = models.CharField(
        max_length=100,
        help_text="e.g., Monday, Wednesday, Friday",
        blank=True
    )
    available_time = models.CharField(
        max_length=100,
        help_text="e.g., 9:00 AM - 5:00 PM",
        blank=True
    )
    
    # Bio
    bio = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Dr. {self.user.get_full_name() or self.user.username}"
    
    class Meta:
        verbose_name = "Doctor Profile"
        verbose_name_plural = "Doctor Profiles"


class DoctorPatientAssignment(models.Model):
    """
    Assigns patients to doctors for access control
    """
    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='assigned_patients',
        limit_choices_to={'role': 'DOCTOR'}
    )
    
    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='assigned_doctors',
        limit_choices_to={'role': 'PATIENT'}
    )
    
    assigned_date = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True, help_text="Assignment notes")
    
    def __str__(self):
        return f"Dr. {self.doctor.username} -> Patient {self.patient.username}"
    
    class Meta:
        verbose_name = "Doctor-Patient Assignment"
        verbose_name_plural = "Doctor-Patient Assignments"
        unique_together = ['doctor', 'patient']
        ordering = ['-assigned_date']