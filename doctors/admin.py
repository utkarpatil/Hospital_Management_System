"""
Admin configuration for Doctor models
"""
from django.contrib import admin
from .models import DoctorProfile, DoctorPatientAssignment

@admin.register(DoctorProfile)
class DoctorProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'specialization', 'license_number', 'experience_years', 'consultation_fee']
    list_filter = ['specialization', 'experience_years']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'license_number']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Professional Information', {
            'fields': ('specialization', 'license_number', 'qualification', 'experience_years')
        }),
        ('Contact & Fees', {
            'fields': ('office_address', 'consultation_fee')
        }),
        ('Availability', {
            'fields': ('available_days', 'available_time')
        }),
        ('About', {
            'fields': ('bio',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(DoctorPatientAssignment)
class DoctorPatientAssignmentAdmin(admin.ModelAdmin):
    list_display = ['doctor', 'patient', 'assigned_date', 'is_active']
    list_filter = ['is_active', 'assigned_date']
    search_fields = ['doctor__username', 'patient__username']
    date_hierarchy = 'assigned_date'
    
    fieldsets = (
        ('Assignment', {
            'fields': ('doctor', 'patient', 'is_active')
        }),
        ('Details', {
            'fields': ('notes', 'assigned_date')
        }),
    )
    readonly_fields = ['assigned_date']