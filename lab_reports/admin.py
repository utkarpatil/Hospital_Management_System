"""
Admin configuration for Lab Report models
"""
from django.contrib import admin
from .models import LabReport, LabTestParameter

class LabTestParameterInline(admin.TabularInline):
    """Inline admin for lab test parameters"""
    model = LabTestParameter
    extra = 1
    fields = ['parameter_name', 'value', 'unit', 'normal_min', 'normal_max', 'is_abnormal']

@admin.register(LabReport)
class LabReportAdmin(admin.ModelAdmin):
    list_display = ['patient', 'doctor', 'test_type', 'test_name', 'test_date', 'is_normal', 'created_at']
    list_filter = ['test_type', 'is_normal', 'test_date', 'created_at']
    search_fields = ['patient__username', 'doctor__username', 'test_name']
    date_hierarchy = 'test_date'
    readonly_fields = ['created_at', 'updated_at']
    inlines = [LabTestParameterInline]
    
    fieldsets = (
        ('Participants', {
            'fields': ('patient', 'doctor')
        }),
        ('Test Information', {
            'fields': ('test_type', 'test_name', 'test_date')
        }),
        ('Results', {
            'fields': ('report_file', 'summary', 'is_normal', 'remarks')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(LabTestParameter)
class LabTestParameterAdmin(admin.ModelAdmin):
    list_display = ['lab_report', 'parameter_name', 'value', 'unit', 'is_abnormal']
    list_filter = ['is_abnormal', 'parameter_name']
    search_fields = ['lab_report__test_name', 'parameter_name']
    
    fieldsets = (
        ('Lab Report', {
            'fields': ('lab_report',)
        }),
        ('Parameter', {
            'fields': ('parameter_name', 'value', 'unit')
        }),
        ('Normal Range', {
            'fields': ('normal_min', 'normal_max', 'is_abnormal')
        }),
    )
    
    def save_model(self, request, obj, form, change):
        """Auto-check if parameter is abnormal before saving"""
        obj.check_abnormal()
        super().save_model(request, obj, form, change)