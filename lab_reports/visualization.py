"""
Visualization Utilities for Lab Reports
Uses Matplotlib to generate charts
"""
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import io
import base64
from datetime import datetime
from .models import LabReport, LabTestParameter


def generate_parameter_trend_chart(patient_id, parameter_name):
    """
    Generate a line chart showing parameter trends over time
    Returns base64 encoded image
    """
    # Get all lab reports with this parameter
    parameters = LabTestParameter.objects.filter(
        lab_report__patient_id=patient_id,
        parameter_name=parameter_name
    ).select_related('lab_report').order_by('lab_report__test_date')
    
    if not parameters.exists():
        return None
    
    # Extract data
    dates = [p.lab_report.test_date for p in parameters]
    values = [float(p.value) for p in parameters]
    
    # Get normal range if available
    normal_min = float(parameters.first().normal_min) if parameters.first().normal_min else None
    normal_max = float(parameters.first().normal_max) if parameters.first().normal_max else None
    unit = parameters.first().unit
    
    # Create plot
    plt.figure(figsize=(10, 6))
    plt.plot(dates, values, marker='o', linewidth=2, markersize=8, label=parameter_name)
    
    # Add normal range
    if normal_min and normal_max:
        plt.axhline(y=normal_min, color='green', linestyle='--', alpha=0.5, label='Normal Min')
        plt.axhline(y=normal_max, color='green', linestyle='--', alpha=0.5, label='Normal Max')
        plt.fill_between(range(len(dates)), normal_min, normal_max, alpha=0.1, color='green')
    
    plt.xlabel('Date', fontsize=12)
    plt.ylabel(f'{parameter_name} ({unit})', fontsize=12)
    plt.title(f'{parameter_name} Trend Over Time', fontsize=14, fontweight='bold')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    # Convert to base64
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.read()).decode()
    plt.close()
    
    return image_base64


def generate_multiple_parameters_chart(patient_id, parameter_names):
    """
    Generate chart comparing multiple parameters
    Returns base64 encoded image
    """
    fig, axes = plt.subplots(len(parameter_names), 1, figsize=(12, 4*len(parameter_names)))
    
    if len(parameter_names) == 1:
        axes = [axes]
    
    for idx, param_name in enumerate(parameter_names):
        parameters = LabTestParameter.objects.filter(
            lab_report__patient_id=patient_id,
            parameter_name=param_name
        ).select_related('lab_report').order_by('lab_report__test_date')
        
        if parameters.exists():
            dates = [p.lab_report.test_date for p in parameters]
            values = [float(p.value) for p in parameters]
            unit = parameters.first().unit
            
            axes[idx].plot(dates, values, marker='o', linewidth=2, markersize=8)
            axes[idx].set_ylabel(f'{param_name} ({unit})', fontsize=10)
            axes[idx].set_title(param_name, fontsize=12, fontweight='bold')
            axes[idx].grid(True, alpha=0.3)
            axes[idx].tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    
    # Convert to base64
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.read()).decode()
    plt.close()
    
    return image_base64


def generate_latest_report_chart(lab_report_id):
    """
    Generate a bar chart for latest lab report parameters
    Returns base64 encoded image
    """
    parameters = LabTestParameter.objects.filter(lab_report_id=lab_report_id)
    
    if not parameters.exists():
        return None
    
    param_names = [p.parameter_name for p in parameters]
    values = [float(p.value) for p in parameters]
    colors = ['red' if p.is_abnormal else 'green' for p in parameters]
    
    plt.figure(figsize=(12, 6))
    bars = plt.bar(param_names, values, color=colors, alpha=0.7)
    
    # Add value labels on bars
    for bar, value in zip(bars, values):
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                f'{value:.2f}',
                ha='center', va='bottom', fontsize=10)
    
    plt.xlabel('Parameters', fontsize=12)
    plt.ylabel('Values', fontsize=12)
    plt.title('Lab Test Results', fontsize=14, fontweight='bold')
    plt.xticks(rotation=45, ha='right')
    plt.grid(True, alpha=0.3, axis='y')
    plt.tight_layout()
    
    # Convert to base64
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.read()).decode()
    plt.close()
    
    return image_base64


def get_parameter_statistics(patient_id, parameter_name):
    """
    Get statistical analysis of a parameter
    """
    parameters = LabTestParameter.objects.filter(
        lab_report__patient_id=patient_id,
        parameter_name=parameter_name
    ).order_by('lab_report__test_date')
    
    if not parameters.exists():
        return None
    
    values = [float(p.value) for p in parameters]
    
    return {
        'parameter_name': parameter_name,
        'unit': parameters.first().unit,
        'count': len(values),
        'latest_value': values[-1],
        'min_value': min(values),
        'max_value': max(values),
        'average': sum(values) / len(values),
        'normal_min': float(parameters.first().normal_min) if parameters.first().normal_min else None,
        'normal_max': float(parameters.first().normal_max) if parameters.first().normal_max else None,
    }