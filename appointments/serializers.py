"""
Serializers for Appointment Management
"""
from rest_framework import serializers
from .models import Appointment
from django.utils import timezone

class AppointmentSerializer(serializers.ModelSerializer):
    """
    Serializer for appointments with full details
    """
    patient_name = serializers.CharField(source='patient.get_full_name', read_only=True)
    doctor_name = serializers.CharField(source='doctor.get_full_name', read_only=True)
    is_past = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Appointment
        fields = [
            'id', 'patient', 'patient_name', 'doctor', 'doctor_name',
            'appointment_date', 'appointment_time', 'duration_minutes',
            'status', 'reason', 'symptoms', 'doctor_notes',
            'is_past', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class AppointmentCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating appointments
    """
    class Meta:
        model = Appointment
        fields = [
            'patient', 'doctor', 'appointment_date', 'appointment_time',
            'duration_minutes', 'reason', 'symptoms'
        ]
    
    def validate(self, data):
        """Validate appointment doesn't conflict with existing ones"""
        doctor = data.get('doctor')
        appointment_date = data.get('appointment_date')
        appointment_time = data.get('appointment_time')
        
        # Check for conflicts
        conflicts = Appointment.objects.filter(
            doctor=doctor,
            appointment_date=appointment_date,
            appointment_time=appointment_time,
            status__in=['PENDING', 'CONFIRMED']
        )
        
        if conflicts.exists():
            raise serializers.ValidationError(
                "This time slot is already booked for this doctor"
            )
        
        return data


class AppointmentUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating appointment status and notes
    """
    class Meta:
        model = Appointment
        fields = ['status', 'doctor_notes']