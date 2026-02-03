"""
Serializers for Doctor Profile and Patient Assignment
"""
from rest_framework import serializers
from .models import DoctorProfile, DoctorPatientAssignment

class DoctorProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for doctor profile
    """
    user_details = serializers.SerializerMethodField()
    
    class Meta:
        model = DoctorProfile
        fields = [
            'id', 'user', 'user_details', 'specialization', 'license_number',
            'qualification', 'experience_years', 'office_address',
            'consultation_fee', 'available_days', 'available_time',
            'bio', 'created_at', 'updated_at'
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


class DoctorPatientAssignmentSerializer(serializers.ModelSerializer):
    """
    Serializer for doctor-patient assignments
    """
    doctor_name = serializers.CharField(source='doctor.get_full_name', read_only=True)
    patient_name = serializers.CharField(source='patient.get_full_name', read_only=True)
    
    class Meta:
        model = DoctorPatientAssignment
        fields = [
            'id', 'doctor', 'doctor_name', 'patient', 'patient_name',
            'assigned_date', 'is_active', 'notes'
        ]
        read_only_fields = ['id', 'assigned_date']


class AssignedPatientSerializer(serializers.Serializer):
    """
    Serializer for listing patients assigned to a doctor
    """
    id = serializers.IntegerField()
    username = serializers.CharField()
    email = serializers.EmailField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    phone = serializers.CharField()
    assigned_date = serializers.DateTimeField()
    is_active = serializers.BooleanField()