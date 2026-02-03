"""
Views for Prescription and Medicine Management
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from .models import Prescription, Medicine
from .serializers import (
    PrescriptionSerializer,
    PrescriptionCreateSerializer,
    MedicineSerializer,
    MedicineReminderSerializer
)
from doctors.permissions import IsDoctor
from patients.permissions import CanCreatePrescription



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def prescription_list(request):
    """
    Get prescriptions for current user
    """
    if request.user.role == 'PATIENT':
        prescriptions = Prescription.objects.filter(patient=request.user)
    elif request.user.role == 'DOCTOR':
        prescriptions = Prescription.objects.filter(doctor=request.user)
    else:
        return Response({
            'error': 'Invalid user role'
        }, status=status.HTTP_403_FORBIDDEN)
    
    serializer = PrescriptionSerializer(prescriptions, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsDoctor])
def create_prescription(request):
    """
    Create a new prescription with medicines (doctors only)
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
    
    serializer = PrescriptionCreateSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(doctor=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def prescription_detail(request, prescription_id):
    """
    Get prescription details with medicines
    """
    prescription = get_object_or_404(Prescription, id=prescription_id)
    
    # Check permissions
    if prescription.patient != request.user and prescription.doctor != request.user:
        return Response({
            'error': 'Access denied'
        }, status=status.HTTP_403_FORBIDDEN)
    
    serializer = PrescriptionSerializer(prescription)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def prescriptions_by_patient(request, patient_id):
    """
    Get all prescriptions for a specific patient
    """
    # Check access permissions
    if request.user.role == 'PATIENT' and request.user.id != patient_id:
        return Response({
            'error': 'You can only view your own prescriptions'
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
    
    prescriptions = Prescription.objects.filter(patient_id=patient_id)
    serializer = PrescriptionSerializer(prescriptions, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def medicine_reminders(request):
    """
    Get active medicine reminders for patient
    """
    if request.user.role != 'PATIENT':
        return Response({
            'error': 'Only patients can view reminders'
        }, status=status.HTTP_403_FORBIDDEN)
    
    from datetime import date, timedelta
    
    # Get prescriptions from last 30 days
    date_threshold = date.today() - timedelta(days=30)
    
    medicines = Medicine.objects.filter(
        prescription__patient=request.user,
        prescription__prescription_date__gte=date_threshold,
        reminder_enabled=True
    ).select_related('prescription')
    
    # Filter medicines that are still active (duration not exceeded)
    active_medicines = []
    today = date.today()
    
    for medicine in medicines:
        prescription_date = medicine.prescription.prescription_date
        end_date = prescription_date + timedelta(days=medicine.duration_days)
        
        if today <= end_date:
            active_medicines.append(medicine)
    
    serializer = MedicineReminderSerializer(active_medicines, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsDoctor])
def add_medicine_to_prescription(request, prescription_id):
    """
    Add a medicine to existing prescription
    """
    prescription = get_object_or_404(Prescription, id=prescription_id)
    
    # Check if doctor owns this prescription
    if prescription.doctor != request.user:
        return Response({
            'error': 'You can only add medicines to your own prescriptions'
        }, status=status.HTTP_403_FORBIDDEN)
    
    serializer = MedicineSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(prescription=prescription)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def medicine_detail(request, medicine_id):
    """
    Get medicine details
    """
    medicine = get_object_or_404(Medicine, id=medicine_id)
    
    # Check permissions
    prescription = medicine.prescription
    if prescription.patient != request.user and prescription.doctor != request.user:
        return Response({
            'error': 'Access denied'
        }, status=status.HTTP_403_FORBIDDEN)
    
    serializer = MedicineSerializer(medicine)
    return Response(serializer.data)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_medicine_reminder(request, medicine_id):
    """
    Update medicine reminder settings (patients only)
    """
    if request.user.role != 'PATIENT':
        return Response({
            'error': 'Only patients can update reminders'
        }, status=status.HTTP_403_FORBIDDEN)
    
    medicine = get_object_or_404(Medicine, id=medicine_id)
    
    if medicine.prescription.patient != request.user:
        return Response({
            'error': 'Access denied'
        }, status=status.HTTP_403_FORBIDDEN)
    
    reminder_enabled = request.data.get('reminder_enabled')
    reminder_times = request.data.get('reminder_times')
    
    if reminder_enabled is not None:
        medicine.reminder_enabled = reminder_enabled
    
    if reminder_times is not None:
        medicine.reminder_times = reminder_times
    
    medicine.save()
    
    serializer = MedicineSerializer(medicine)
    return Response(serializer.data)