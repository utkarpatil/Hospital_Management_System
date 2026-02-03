"""
Views for Lab Report Management and Visualization
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from .models import LabReport, LabTestParameter
from .serializers import (
    LabReportSerializer,
    LabReportCreateSerializer,
    LabTestParameterSerializer
)
from .visualization import (
    generate_parameter_trend_chart,
    generate_multiple_parameters_chart,
    generate_latest_report_chart,
    get_parameter_statistics
)
from doctors.permissions import IsDoctor



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def lab_report_list(request):
    """
    Get lab reports for current user
    """
    if request.user.role == 'PATIENT':
        reports = LabReport.objects.filter(patient=request.user)
    elif request.user.role == 'DOCTOR':
        # Get reports for assigned patients
        from doctors.models import DoctorPatientAssignment
        assigned_patients = DoctorPatientAssignment.objects.filter(
            doctor=request.user,
            is_active=True
        ).values_list('patient_id', flat=True)
        reports = LabReport.objects.filter(patient_id__in=assigned_patients)
    else:
        return Response({
            'error': 'Invalid user role'
        }, status=status.HTTP_403_FORBIDDEN)
    
    # Optional filters
    test_type = request.query_params.get('test_type')
    if test_type:
        reports = reports.filter(test_type=test_type)
    
    date_from = request.query_params.get('date_from')
    if date_from:
        reports = reports.filter(test_date__gte=date_from)
    
    date_to = request.query_params.get('date_to')
    if date_to:
        reports = reports.filter(test_date__lte=date_to)
    
    serializer = LabReportSerializer(reports, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsDoctor])
def create_lab_report(request):
    """
    Create a new lab report (doctors only)
    """
    # Verify doctor is assigned to patient
    from doctors.models import DoctorPatientAssignment
    
    patient_id = request.data.get('patient')
    if not patient_id:
        return Response({
            'error': 'patient is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    is_assigned = DoctorPatientAssignment.objects.filter(
        doctor=request.user,
        patient_id=patient_id,
        is_active=True
    ).exists()
    
    if not is_assigned:
        return Response({
            'error': 'You are not assigned to this patient'
        }, status=status.HTTP_403_FORBIDDEN)
    
    serializer = LabReportCreateSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(doctor=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def lab_report_detail(request, report_id):
    """
    Get lab report details with parameters
    """
    report = get_object_or_404(LabReport, id=report_id)
    
    # Check permissions
    if request.user.role == 'PATIENT' and report.patient != request.user:
        return Response({
            'error': 'Access denied'
        }, status=status.HTTP_403_FORBIDDEN)
    
    if request.user.role == 'DOCTOR':
        from doctors.models import DoctorPatientAssignment
        is_assigned = DoctorPatientAssignment.objects.filter(
            doctor=request.user,
            patient=report.patient,
            is_active=True
        ).exists()
        
        if not is_assigned:
            return Response({
                'error': 'Access denied'
            }, status=status.HTTP_403_FORBIDDEN)
    
    serializer = LabReportSerializer(report)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def reports_by_patient(request, patient_id):
    """
    Get all lab reports for a specific patient
    """
    # Check access permissions
    if request.user.role == 'PATIENT' and request.user.id != patient_id:
        return Response({
            'error': 'You can only view your own reports'
        }, status=status.HTTP_403_FORBIDDEN)
    
    if request.user.role == 'DOCTOR':
        from doctors.models import DoctorPatientAssignment
        is_assigned = DoctorPatientAssignment.objects.filter(
            doctor=request.user,
            patient_id=patient_id,
            is_active=True
        ).exists()
        
        if not is_assigned:
            return Response({
                'error': 'You do not have access to this patient'
            }, status=status.HTTP_403_FORBIDDEN)
    
    reports = LabReport.objects.filter(patient_id=patient_id)
    serializer = LabReportSerializer(reports, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def visualize_parameter_trend(request, patient_id):
    """
    Generate trend chart for a specific parameter
    """
    # Check permissions
    if request.user.role == 'PATIENT' and request.user.id != patient_id:
        return Response({
            'error': 'Access denied'
        }, status=status.HTTP_403_FORBIDDEN)
    
    if request.user.role == 'DOCTOR':
        from doctors.models import DoctorPatientAssignment
        is_assigned = DoctorPatientAssignment.objects.filter(
            doctor=request.user,
            patient_id=patient_id,
            is_active=True
        ).exists()
        
        if not is_assigned:
            return Response({
                'error': 'Access denied'
            }, status=status.HTTP_403_FORBIDDEN)
    
    parameter_name = request.query_params.get('parameter')
    if not parameter_name:
        return Response({
            'error': 'parameter query parameter is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    chart_image = generate_parameter_trend_chart(patient_id, parameter_name)
    
    if not chart_image:
        return Response({
            'error': 'No data available for this parameter'
        }, status=status.HTTP_404_NOT_FOUND)
    
    return Response({
        'parameter': parameter_name,
        'chart': f'data:image/png;base64,{chart_image}'
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def visualize_report(request, report_id):
    """
    Generate visualization for a specific lab report
    """
    report = get_object_or_404(LabReport, id=report_id)
    
    # Check permissions
    if request.user.role == 'PATIENT' and report.patient != request.user:
        return Response({
            'error': 'Access denied'
        }, status=status.HTTP_403_FORBIDDEN)
    
    if request.user.role == 'DOCTOR':
        from doctors.models import DoctorPatientAssignment
        is_assigned = DoctorPatientAssignment.objects.filter(
            doctor=request.user,
            patient=report.patient,
            is_active=True
        ).exists()
        
        if not is_assigned:
            return Response({
                'error': 'Access denied'
            }, status=status.HTTP_403_FORBIDDEN)
    
    chart_image = generate_latest_report_chart(report_id)
    
    if not chart_image:
        return Response({
            'error': 'No parameters available for visualization'
        }, status=status.HTTP_404_NOT_FOUND)
    
    return Response({
        'report_id': report_id,
        'test_name': report.test_name,
        'chart': f'data:image/png;base64,{chart_image}'
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def parameter_statistics(request, patient_id):
    """
    Get statistical analysis for a parameter
    """
    # Check permissions
    if request.user.role == 'PATIENT' and request.user.id != patient_id:
        return Response({
            'error': 'Access denied'
        }, status=status.HTTP_403_FORBIDDEN)
    
    if request.user.role == 'DOCTOR':
        from doctors.models import DoctorPatientAssignment
        is_assigned = DoctorPatientAssignment.objects.filter(
            doctor=request.user,
            patient_id=patient_id,
            is_active=True
        ).exists()
        
        if not is_assigned:
            return Response({
                'error': 'Access denied'
            }, status=status.HTTP_403_FORBIDDEN)
    
    parameter_name = request.query_params.get('parameter')
    if not parameter_name:
        return Response({
            'error': 'parameter query parameter is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    stats = get_parameter_statistics(patient_id, parameter_name)
    
    if not stats:
        return Response({
            'error': 'No data available for this parameter'
        }, status=status.HTTP_404_NOT_FOUND)
    
    return Response(stats)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def available_parameters(request, patient_id):
    """
    Get list of all available parameters for a patient
    """
    # Check permissions
    if request.user.role == 'PATIENT' and request.user.id != patient_id:
        return Response({
            'error': 'Access denied'
        }, status=status.HTTP_403_FORBIDDEN)
    
    if request.user.role == 'DOCTOR':
        from doctors.models import DoctorPatientAssignment
        is_assigned = DoctorPatientAssignment.objects.filter(
            doctor=request.user,
            patient_id=patient_id,
            is_active=True
        ).exists()
        
        if not is_assigned:
            return Response({
                'error': 'Access denied'
            }, status=status.HTTP_403_FORBIDDEN)
    
    parameters = LabTestParameter.objects.filter(
        lab_report__patient_id=patient_id
    ).values_list('parameter_name', flat=True).distinct()
    
    return Response({
        'patient_id': patient_id,
        'parameters': list(parameters)
    })