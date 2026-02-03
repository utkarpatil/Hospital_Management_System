"""
Serializers for Patient Profile and Medical History
"""
from rest_framework import serializers
from .models import PatientProfile, MedicalHistory
from django.contrib.auth import get_user_model

User = get_user_model()

class PatientProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for patient profile
    """
    user_details = serializers.SerializerMethodField()
    
    class Meta:
        model = PatientProfile
        fields = [
            'id', 'user', 'user_details', 'gender', 'blood_group',
            'height', 'weight', 'address', 'emergency_contact',
            'emergency_contact_name', 'allergies', 'chronic_conditions',
            'current_medications', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']
    
    def get_user_details(self, obj):
        """Get basic user information"""
        return {
            'username': obj.user.username,
            'email': obj.user.email,
            'first_name': obj.user.first_name,
            'last_name': obj.user.last_name,
            'phone': obj.user.phone,
        }


class MedicalHistorySerializer(serializers.ModelSerializer):
    """
    Serializer for medical history entries
    """
    patient_name = serializers.CharField(source='patient.get_full_name', read_only=True)
    doctor_name = serializers.CharField(source='doctor.get_full_name', read_only=True)
    
    class Meta:
        model = MedicalHistory
        fields = [
            'id', 'patient', 'patient_name', 'doctor', 'doctor_name',
            'entry_type', 'title', 'description', 'date', 'attachments',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class MedicalHistoryCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating medical history entries
    """
    class Meta:
        model = MedicalHistory
        fields = [
            'patient', 'doctor', 'entry_type', 'title',
            'description', 'date', 'attachments'
        ]