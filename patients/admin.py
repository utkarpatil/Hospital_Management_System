"""
Admin configuration for Patient models
"""
from django.contrib import admin
from .models import PatientProfile, MedicalHistory

@admin.register(PatientProfile)
class PatientProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'gender', 'blood_group', 'created_at']
    list_filter = ['gender', 'blood_group', 'created_at']
    search_fields = ['user__username', 'user__first_name', 'user__last_name']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Personal Information', {
            'fields': ('gender', 'blood_group', 'height', 'weight')
        }),
        ('Contact Information', {
            'fields': ('address', 'emergency_contact', 'emergency_contact_name')
        }),
        ('Medical Background', {
            'fields': ('allergies', 'chronic_conditions', 'current_medications')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(MedicalHistory)
class MedicalHistoryAdmin(admin.ModelAdmin):
    list_display = ['patient', 'doctor', 'entry_type', 'title', 'date', 'created_at']
    list_filter = ['entry_type', 'date', 'created_at']
    search_fields = ['patient__username', 'doctor__username', 'title', 'description']
    date_hierarchy = 'date'
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Participants', {
            'fields': ('patient', 'doctor')
        }),
        ('Entry Details', {
            'fields': ('entry_type', 'title', 'description', 'date')
        }),
        ('Attachments', {
            'fields': ('attachments',)
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )