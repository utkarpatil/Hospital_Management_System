"""
Views for Doctor Profile and Patient Assignment
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

from .models import DoctorProfile, DoctorPatientAssignment
from .serializers import (
    DoctorProfileSerializer,
    DoctorPatientAssignmentSerializer,
    AssignedPatientSerializer
)
from .permissions import IsDoctor

User = get_user_model()


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated, IsDoctor])
def doctor_profile(request):
    """
    Get or create doctor profile for current user
    """
    if request.method == 'GET':
        try:
            profile = DoctorProfile.objects.get(user=request.user)
            serializer = DoctorProfileSerializer(profile)
            return Response(serializer.data)
        except DoctorProfile.DoesNotExist:
            return Response({
                'message': 'Profile not created yet'
            }, status=status.HTTP_404_NOT_FOUND)
    
    elif request.method == 'POST':
        if DoctorProfile.objects.filter(user=request.user).exists():
            return Response({
                'error': 'Profile already exists. Use PUT to update.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = DoctorProfileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated, IsDoctor])
def update_doctor_profile(request):
    """
    Update doctor profile
    """
    try:
        profile = DoctorProfile.objects.get(user=request.user)
    except DoctorProfile.DoesNotExist:
        return Response({
            'error': 'Profile does not exist. Create one first.'
        }, status=status.HTTP_404_NOT_FOUND)
    
    serializer = DoctorProfileSerializer(profile, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def doctor_list(request):
    """
    Get list of all doctors (for patient booking)
    """
    doctors = DoctorProfile.objects.select_related('user').all()
    serializer = DoctorProfileSerializer(doctors, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def doctor_detail(request, doctor_id):
    """
    Get doctor profile by ID
    """
    profile = get_object_or_404(DoctorProfile, user_id=doctor_id)
    serializer = DoctorProfileSerializer(profile)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsDoctor])
def assigned_patients(request):
    """
    Get list of patients assigned to current doctor
    """
    assignments = DoctorPatientAssignment.objects.filter(
        doctor=request.user,
        is_active=True
    ).select_related('patient')
    
    patients_data = []
    for assignment in assignments:
        patient = assignment.patient
        patients_data.append({
            'id': patient.id,
            'username': patient.username,
            'email': patient.email,
            'first_name': patient.first_name,
            'last_name': patient.last_name,
            'phone': patient.phone,
            'assigned_date': assignment.assigned_date,
            'is_active': assignment.is_active
        })
    
    serializer = AssignedPatientSerializer(patients_data, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsDoctor])
def assign_patient(request):
    """
    Assign a patient to current doctor
    """
    patient_id = request.data.get('patient_id')
    notes = request.data.get('notes', '')
    
    if not patient_id:
        return Response({
            'error': 'patient_id is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        patient = User.objects.get(id=patient_id, role='PATIENT')
    except User.DoesNotExist:
        return Response({
            'error': 'Patient not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Check if already assigned
    existing = DoctorPatientAssignment.objects.filter(
        doctor=request.user,
        patient=patient
    ).first()
    
    if existing:
        if existing.is_active:
            return Response({
                'error': 'Patient is already assigned to you'
            }, status=status.HTTP_400_BAD_REQUEST)
        else:
            # Reactivate the assignment
            existing.is_active = True
            existing.notes = notes
            existing.save()
            serializer = DoctorPatientAssignmentSerializer(existing)
            return Response(serializer.data)
    
    # Create new assignment
    assignment = DoctorPatientAssignment.objects.create(
        doctor=request.user,
        patient=patient,
        notes=notes
    )
    
    serializer = DoctorPatientAssignmentSerializer(assignment)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsDoctor])
def unassign_patient(request, patient_id):
    """
    Unassign a patient from current doctor
    """
    try:
        assignment = DoctorPatientAssignment.objects.get(
            doctor=request.user,
            patient_id=patient_id,
            is_active=True
        )
        assignment.is_active = False
        assignment.save()
        
        return Response({
            'message': 'Patient unassigned successfully'
        })
    except DoctorPatientAssignment.DoesNotExist:
        return Response({
            'error': 'Assignment not found'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_doctors(request):
    """
    Search doctors by specialization or name
    """
    specialization = request.query_params.get('specialization', '')
    name = request.query_params.get('name', '')
    
    doctors = DoctorProfile.objects.select_related('user').all()
    
    if specialization:
        doctors = doctors.filter(specialization__icontains=specialization)
    
    if name:
        doctors = doctors.filter(
            user__first_name__icontains=name
        ) | doctors.filter(
            user__last_name__icontains=name
        )
    
    serializer = DoctorProfileSerializer(doctors, many=True)
    return Response(serializer.data)