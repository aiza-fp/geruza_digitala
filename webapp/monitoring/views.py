from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from datetime import timedelta
import csv
from .models import MqttData
from .decorators import role_required


@login_required
def dashboard(request):
    """Dashboard showing all hosts."""
    hosts = MqttData.get_distinct_hosts()
    
    context = {
        'hosts': hosts,
        'user_role': request.user.role,
    }
    return render(request, 'monitoring/dashboard.html', context)


@login_required
def host_detail(request, host_id):
    """Detail view for a specific host showing all topics."""
    topics = MqttData.get_topics_for_host(host_id)
    
    # Group topics by prefix for better organization
    topic_groups = {}
    for topic in topics:
        topic_name = topic['topic']
        if '/' in topic_name:
            prefix = topic_name.split('/')[0]
            if prefix not in topic_groups:
                topic_groups[prefix] = []
            topic_groups[prefix].append(topic_name)
        else:
            if 'other' not in topic_groups:
                topic_groups['other'] = []
            topic_groups['other'].append(topic_name)
    
    context = {
        'host_id': host_id,
        'topic_groups': topic_groups,
        'user_role': request.user.role,
    }
    return render(request, 'monitoring/host_detail.html', context)


@login_required
def topic_field_selection(request, host_id, topic_name):
    """Field selection view for a specific topic."""
    # Get available numeric fields for this topic
    available_fields = MqttData.get_numeric_columns_for_topic(host_id, topic_name)
    
    if not available_fields:
        context = {
            'host_id': host_id,
            'topic_name': topic_name,
            'available_fields': [],
            'user_role': request.user.role,
            'no_fields': True,
        }
        return render(request, 'monitoring/topic_field_selection.html', context)
    
    context = {
        'host_id': host_id,
        'topic_name': topic_name,
        'available_fields': available_fields,
        'user_role': request.user.role,
        'no_fields': False,
    }
    return render(request, 'monitoring/topic_field_selection.html', context)


@login_required
def topic_chart(request, host_id, topic_name, field_name):
    """Chart view for a specific topic and field with time series data."""
    # Get time range from request
    time_range = request.GET.get('range', '5m')
    
    # Calculate start time based on range
    now = timezone.now()
    if time_range == '5m':
        start_time = now - timedelta(minutes=5)
    elif time_range == '1h':
        start_time = now - timedelta(hours=1)
    elif time_range == '24h':
        start_time = now - timedelta(days=1)
    elif time_range == '7d':
        start_time = now - timedelta(days=7)
    elif time_range == '30d':
        start_time = now - timedelta(days=30)
    else:
        start_time = now - timedelta(minutes=5)  # Default to 5 minutes
    
    # Get time series data with the selected field
    data = MqttData.get_time_series_data_with_field(host_id, topic_name, field_name, start_time)
    
    context = {
        'host_id': host_id,
        'topic_name': topic_name,
        'field_name': field_name,
        'time_range': time_range,
        'data_count': len(data),
        'user_role': request.user.role,
    }
    return render(request, 'monitoring/topic_chart.html', context)


@login_required
def api_chart_data(request, host_id, topic_name, field_name):
    """API endpoint for chart data."""
    # Get time range from request
    time_range = request.GET.get('range', '5m')
    
    # Calculate start time based on range
    now = timezone.now()
    if time_range == '5m':
        start_time = now - timedelta(minutes=5)
    elif time_range == '1h':
        start_time = now - timedelta(hours=1)
    elif time_range == '24h':
        start_time = now - timedelta(days=1)
    elif time_range == '7d':
        start_time = now - timedelta(days=7)
    elif time_range == '30d':
        start_time = now - timedelta(days=30)
    else:
        start_time = now - timedelta(minutes=5)  # Default to 5 minutes
    
    # Get time series data with the selected field
    data = MqttData.get_time_series_data_with_field(host_id, topic_name, field_name, start_time)
    
    # Prepare data for Chart.js
    chart_data = {
        'labels': [],
        'datasets': [{
            'label': f'{topic_name} ({field_name})',
            'data': [],
            'borderColor': 'rgb(75, 192, 192)',
            'backgroundColor': 'rgba(75, 192, 192, 0.2)',
            'tension': 0.1
        }]
    }
    
    for time_val, field_val in data:
        # Convert datetime to simple string format to avoid Chart.js time scale detection
        chart_data['labels'].append(time_val.strftime('%Y-%m-%d %H:%M:%S'))
        chart_data['datasets'][0]['data'].append(float(field_val) if field_val is not None else None)
    
    return JsonResponse(chart_data)


@role_required(['admin', 'editor'])
def export_csv(request, host_id, topic_name, field_name):
    """Export topic data to CSV (Admin/Editor only)."""
    # Get time range from request
    time_range = request.GET.get('range', '5m')
    
    # Calculate start time based on range
    now = timezone.now()
    if time_range == '5m':
        start_time = now - timedelta(minutes=5)
    elif time_range == '1h':
        start_time = now - timedelta(hours=1)
    elif time_range == '24h':
        start_time = now - timedelta(days=1)
    elif time_range == '7d':
        start_time = now - timedelta(days=7)
    elif time_range == '30d':
        start_time = now - timedelta(days=30)
    else:
        start_time = now - timedelta(minutes=5)  # Default to 5 minutes
    
    # Get time series data with the selected field
    data = MqttData.get_time_series_data_with_field(host_id, topic_name, field_name, start_time)
    
    # Create CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{host_id}_{topic_name.replace("/", "_")}_{field_name}.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Time', 'Host', 'Topic', field_name.title()])
    
    for time_val, field_val in data:
        writer.writerow([
            time_val.isoformat(),
            host_id,
            topic_name,
            field_val
        ])
    
    return response