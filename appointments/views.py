"""
Views for Appointment Management
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from datetime import datetime

from .models import Appointment
from .serializers import (
    AppointmentSerializer,
    AppointmentCreateSerializer,
    AppointmentUpdateSerializer
)
from patients.permissions import IsPatient
from doctors.permissions import IsDoctor


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def appointment_list(request):
    """
    Get appointments for current user
    """
    if request.user.role == 'PATIENT':
        appointments = Appointment.objects.filter(patient=request.user)
    elif request.user.role == 'DOCTOR':
        appointments = Appointment.objects.filter(doctor=request.user)
    else:
        return Response({
            'error': 'Invalid user role'
        }, status=status.HTTP_403_FORBIDDEN)
    
    # Optional filters
    status_filter = request.query_params.get('status')
    if status_filter:
        appointments = appointments.filter(status=status_filter)
    
    date_from = request.query_params.get('date_from')
    if date_from:
        appointments = appointments.filter(appointment_date__gte=date_from)
    
    date_to = request.query_params.get('date_to')
    if date_to:
        appointments = appointments.filter(appointment_date__lte=date_to)
    
    serializer = AppointmentSerializer(appointments, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsPatient])
def create_appointment(request):
    """
    Create a new appointment (patients only)
    """
    serializer = AppointmentCreateSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(patient=request.user, status='PENDING')
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def appointment_detail(request, appointment_id):
    """
    Get appointment details
    """
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    # Check permissions
    if appointment.patient != request.user and appointment.doctor != request.user:
        return Response({
            'error': 'Access denied'
        }, status=status.HTTP_403_FORBIDDEN)
    
    serializer = AppointmentSerializer(appointment)
    return Response(serializer.data)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_appointment_status(request, appointment_id):
    """
    Update appointment status (doctors can confirm/complete, patients can cancel)
    """
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    # Check permissions
    if appointment.patient != request.user and appointment.doctor != request.user:
        return Response({
            'error': 'Access denied'
        }, status=status.HTTP_403_FORBIDDEN)
    
    new_status = request.data.get('status')
    
    # Patients can only cancel their appointments
    if request.user.role == 'PATIENT':
        if new_status != 'CANCELLED':
            return Response({
                'error': 'Patients can only cancel appointments'
            }, status=status.HTTP_403_FORBIDDEN)
    
    # Doctors can update status and add notes
    if request.user.role == 'DOCTOR':
        serializer = AppointmentUpdateSerializer(appointment, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # For patients (cancellation)
    appointment.status = new_status
    appointment.save()
    
    serializer = AppointmentSerializer(appointment)
    return Response(serializer.data)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated, IsPatient])
def cancel_appointment(request, appointment_id):
    """
    Cancel an appointment (patients only)
    """
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    if appointment.patient != request.user:
        return Response({
            'error': 'Access denied'
        }, status=status.HTTP_403_FORBIDDEN)
    
    if appointment.status == 'COMPLETED':
        return Response({
            'error': 'Cannot cancel completed appointments'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    appointment.status = 'CANCELLED'
    appointment.save()
    
    return Response({
        'message': 'Appointment cancelled successfully'
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsDoctor])
def upcoming_appointments(request):
    """
    Get upcoming appointments for doctor
    """
    from datetime import date
    today = date.today()
    
    appointments = Appointment.objects.filter(
        doctor=request.user,
        appointment_date__gte=today,
        status__in=['PENDING', 'CONFIRMED']
    ).order_by('appointment_date', 'appointment_time')
    
    serializer = AppointmentSerializer(appointments, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsDoctor])
def pending_appointments(request):
    """
    Get pending appointment requests for doctor
    """
    appointments = Appointment.objects.filter(
        doctor=request.user,
        status='PENDING'
    ).order_by('appointment_date', 'appointment_time')
    
    serializer = AppointmentSerializer(appointments, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def available_slots(request, doctor_id):
    """
    Get available time slots for a doctor on a specific date
    """
    appointment_date = request.query_params.get('date')
    
    if not appointment_date:
        return Response({
            'error': 'date parameter is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Get booked slots
    booked_appointments = Appointment.objects.filter(
        doctor_id=doctor_id,
        appointment_date=appointment_date,
        status__in=['PENDING', 'CONFIRMED']
    ).values_list('appointment_time', flat=True)
    
    # Generate time slots (9 AM to 5 PM, 30-minute intervals)
    from datetime import time, timedelta
    
    available_slots = []
    current_time = time(9, 0)
    end_time = time(17, 0)
    
    while current_time < end_time:
        if current_time not in booked_appointments:
            available_slots.append(current_time.strftime('%H:%M'))
        
        # Add 30 minutes
        current_datetime = datetime.combine(datetime.today(), current_time)
        current_datetime += timedelta(minutes=30)
        current_time = current_datetime.time()
    
    return Response({
        'date': appointment_date,
        'doctor_id': doctor_id,
        'available_slots': available_slots
    })