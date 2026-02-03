"""
Serializers for Prescription and Medicine Management
"""
from rest_framework import serializers
from .models import Prescription, Medicine

class MedicineSerializer(serializers.ModelSerializer):
    """
    Serializer for medicine details
    """
    class Meta:
        model = Medicine
        fields = [
            'id', 'prescription', 'medicine_name', 'dosage', 'dosage_form',
            'frequency', 'duration_days', 'instructions', 'reminder_enabled',
            'reminder_times', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class PrescriptionSerializer(serializers.ModelSerializer):
    """
    Serializer for prescription with medicines
    """
    patient_name = serializers.CharField(source='patient.get_full_name', read_only=True)
    doctor_name = serializers.CharField(source='doctor.get_full_name', read_only=True)
    medicines = MedicineSerializer(many=True, read_only=True)
    
    class Meta:
        model = Prescription
        fields = [
            'id', 'patient', 'patient_name', 'doctor', 'doctor_name',
            'diagnosis', 'notes', 'prescription_date', 'medicines',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'prescription_date', 'created_at', 'updated_at']


class PrescriptionCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating prescriptions
    """
    medicines = MedicineSerializer(many=True, write_only=True)
    
    class Meta:
        model = Prescription
        fields = ['patient', 'doctor', 'diagnosis', 'notes', 'medicines']
    
    def create(self, validated_data):
        """Create prescription with medicines"""
        medicines_data = validated_data.pop('medicines')
        prescription = Prescription.objects.create(**validated_data)
        
        # Create medicines
        for medicine_data in medicines_data:
            Medicine.objects.create(prescription=prescription, **medicine_data)
        
        return prescription


class MedicineReminderSerializer(serializers.ModelSerializer):
    """
    Serializer for medicine reminders
    """
    prescription_diagnosis = serializers.CharField(source='prescription.diagnosis', read_only=True)
    
    class Meta:
        model = Medicine
        fields = [
            'id', 'medicine_name', 'dosage', 'frequency', 'instructions',
            'reminder_times', 'prescription_diagnosis'
        ]