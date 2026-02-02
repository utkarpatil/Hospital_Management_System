"""
Prescription and Medicine Models
"""
from django.db import models
from django.conf import settings

class Prescription(models.Model):
    """
    Prescription created by doctors for patients
    """
    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='prescriptions',
        limit_choices_to={'role': 'PATIENT'}
    )
    
    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='prescriptions_created',
        limit_choices_to={'role': 'DOCTOR'}
    )
    
    # Prescription Details
    diagnosis = models.CharField(max_length=200)
    notes = models.TextField(blank=True, help_text="Additional instructions or notes")
    prescription_date = models.DateField(auto_now_add=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Prescription for {self.patient.username} by Dr. {self.doctor.username} - {self.prescription_date}"
    
    class Meta:
        verbose_name = "Prescription"
        verbose_name_plural = "Prescriptions"
        ordering = ['-prescription_date']


class Medicine(models.Model):
    """
    Medicines assigned in prescriptions
    """
    FREQUENCY_CHOICES = (
        ('ONCE_DAILY', 'Once Daily'),
        ('TWICE_DAILY', 'Twice Daily'),
        ('THREE_TIMES', 'Three Times Daily'),
        ('FOUR_TIMES', 'Four Times Daily'),
        ('AS_NEEDED', 'As Needed'),
        ('BEFORE_MEALS', 'Before Meals'),
        ('AFTER_MEALS', 'After Meals'),
    )
    
    DOSAGE_FORM_CHOICES = (
        ('TABLET', 'Tablet'),
        ('CAPSULE', 'Capsule'),
        ('SYRUP', 'Syrup'),
        ('INJECTION', 'Injection'),
        ('DROPS', 'Drops'),
        ('CREAM', 'Cream'),
        ('OINTMENT', 'Ointment'),
    )
    
    prescription = models.ForeignKey(
        Prescription,
        on_delete=models.CASCADE,
        related_name='medicines'
    )
    
    # Medicine Details
    medicine_name = models.CharField(max_length=200)
    dosage = models.CharField(max_length=100, help_text="e.g., 500mg")
    dosage_form = models.CharField(max_length=20, choices=DOSAGE_FORM_CHOICES, default='TABLET')
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES)
    duration_days = models.PositiveIntegerField(help_text="Duration in days")
    
    # Instructions
    instructions = models.TextField(blank=True, help_text="Special instructions for taking medicine")
    
    # Reminder Settings
    reminder_enabled = models.BooleanField(default=True)
    reminder_times = models.CharField(
        max_length=200,
        blank=True,
        help_text="Comma-separated times for reminders, e.g., 08:00,14:00,20:00"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.medicine_name} - {self.dosage} ({self.frequency})"
    
    class Meta:
        verbose_name = "Medicine"
        verbose_name_plural = "Medicines"
        ordering = ['medicine_name']

class Appointment(models.Model):
    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='patient_appointments',
        limit_choices_to={'role': 'PATIENT'}
    )

    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='doctor_appointments',
        limit_choices_to={'role': 'DOCTOR'}
    )

    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    duration_minutes = models.PositiveIntegerField(default=15)

    status = models.CharField(
        max_length=20,
        choices=(
            ('PENDING', 'Pending'),
            ('CONFIRMED', 'Confirmed'),
            ('COMPLETED', 'Completed'),
            ('CANCELLED', 'Cancelled'),
        ),
        default='PENDING'
    )

    reason = models.CharField(max_length=255)
    symptoms = models.TextField(blank=True)
    doctor_notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.patient.username} with Dr. {self.doctor.username} on {self.appointment_date}"
