"""
Lab Report Models with Data Visualization
"""
from django.db import models
from django.conf import settings

class LabReport(models.Model):
    """
    Lab reports and test results
    """
    TEST_TYPE_CHOICES = (
        ('BLOOD', 'Blood Test'),
        ('URINE', 'Urine Test'),
        ('XRAY', 'X-Ray'),
        ('MRI', 'MRI Scan'),
        ('CT', 'CT Scan'),
        ('ECG', 'ECG'),
        ('ULTRASOUND', 'Ultrasound'),
        ('OTHER', 'Other'),
    )
    
    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='lab_reports',
        limit_choices_to={'role': 'PATIENT'}
    )
    
    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='lab_reports_ordered',
        limit_choices_to={'role': 'DOCTOR'}
    )
    
    # Report Details
    test_type = models.CharField(max_length=20, choices=TEST_TYPE_CHOICES)
    test_name = models.CharField(max_length=200)
    test_date = models.DateField()
    
    # Results
    report_file = models.FileField(upload_to='lab_reports/', blank=True, null=True)
    summary = models.TextField(blank=True, help_text="Brief summary of findings")
    
    # Status
    is_normal = models.BooleanField(default=True, help_text="Are results within normal range?")
    remarks = models.TextField(blank=True, help_text="Doctor's remarks on the report")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.test_name} - {self.patient.username} - {self.test_date}"
    
    class Meta:
        verbose_name = "Lab Report"
        verbose_name_plural = "Lab Reports"
        ordering = ['-test_date']


class LabTestParameter(models.Model):
    """
    Individual test parameters for visualization
    """
    lab_report = models.ForeignKey(
        LabReport,
        on_delete=models.CASCADE,
        related_name='parameters'
    )
    
    # Parameter Details
    parameter_name = models.CharField(max_length=100, help_text="e.g., Hemoglobin, Blood Sugar")
    value = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=50, help_text="e.g., mg/dL, g/dL")
    
    # Reference Range
    normal_min = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    normal_max = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    
    # Status
    is_abnormal = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.parameter_name}: {self.value} {self.unit}"
    
    def check_abnormal(self):
        """Check if value is outside normal range"""
        if self.normal_min and self.normal_max:
            self.is_abnormal = not (self.normal_min <= self.value <= self.normal_max)
        return self.is_abnormal
    
    class Meta:
        verbose_name = "Lab Test Parameter"
        verbose_name_plural = "Lab Test Parameters"
        ordering = ['parameter_name']