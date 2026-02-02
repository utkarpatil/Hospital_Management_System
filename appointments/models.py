"""
Appointment Management Models
"""
from django.db import models
from django.conf import settings
from django.utils import timezone

class Appointment(models.Model):
    """
    Appointment booking and management
    """
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('CONFIRMED', 'Confirmed'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    )
    
    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='appointments_as_patient',
        limit_choices_to={'role': 'PATIENT'}
    )
    
    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='appointments_as_doctor',
        limit_choices_to={'role': 'DOCTOR'}
    )
    
    # Appointment Details
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    duration_minutes = models.PositiveIntegerField(default=30, help_text="Duration in minutes")
    
    # Status and Notes
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    reason = models.TextField(help_text="Reason for appointment")
    symptoms = models.TextField(blank=True, help_text="Patient's symptoms")
    doctor_notes = models.TextField(blank=True, help_text="Doctor's notes after consultation")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.patient.username} with Dr. {self.doctor.username} on {self.appointment_date}"
    
    @property
    def is_past(self):
        """Check if appointment date/time has passed"""
        appointment_datetime = timezone.datetime.combine(
            self.appointment_date, 
            self.appointment_time
        )
        return appointment_datetime < timezone.now()
    
    class Meta:
        verbose_name = "Appointment"
        verbose_name_plural = "Appointments"
        ordering = ['-appointment_date', '-appointment_time']
        unique_together = ['doctor', 'appointment_date', 'appointment_time']