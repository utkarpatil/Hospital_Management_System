"""
Serializers for Lab Reports and Visualization
"""
from rest_framework import serializers
from .models import LabReport, LabTestParameter

class LabTestParameterSerializer(serializers.ModelSerializer):
    """
    Serializer for lab test parameters
    """
    class Meta:
        model = LabTestParameter
        fields = [
            'id', 'lab_report', 'parameter_name', 'value', 'unit',
            'normal_min', 'normal_max', 'is_abnormal'
        ]
        read_only_fields = ['id']


class LabReportSerializer(serializers.ModelSerializer):
    """
    Serializer for lab reports with parameters
    """
    patient_name = serializers.CharField(source='patient.get_full_name', read_only=True)
    doctor_name = serializers.CharField(source='doctor.get_full_name', read_only=True)
    parameters = LabTestParameterSerializer(many=True, read_only=True)
    
    class Meta:
        model = LabReport
        fields = [
            'id', 'patient', 'patient_name', 'doctor', 'doctor_name',
            'test_type', 'test_name', 'test_date', 'report_file',
            'summary', 'is_normal', 'remarks', 'parameters',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class LabReportCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating lab reports
    """
    parameters = LabTestParameterSerializer(many=True, write_only=True, required=False)
    
    class Meta:
        model = LabReport
        fields = [
            'patient', 'doctor', 'test_type', 'test_name', 'test_date',
            'report_file', 'summary', 'is_normal', 'remarks', 'parameters'
        ]
    
    def create(self, validated_data):
        """Create lab report with parameters"""
        parameters_data = validated_data.pop('parameters', [])
        lab_report = LabReport.objects.create(**validated_data)
        
        # Create parameters
        for parameter_data in parameters_data:
            param = LabTestParameter.objects.create(
                lab_report=lab_report,
                **parameter_data
            )
            param.check_abnormal()
            param.save()
        
        return lab_report


class LabReportVisualizationSerializer(serializers.Serializer):
    """
    Serializer for lab report visualization data
    """
    parameter_name = serializers.CharField()
    values = serializers.ListField(child=serializers.FloatField())
    dates = serializers.ListField(child=serializers.DateField())
    normal_min = serializers.FloatField(allow_null=True)
    normal_max = serializers.FloatField(allow_null=True)