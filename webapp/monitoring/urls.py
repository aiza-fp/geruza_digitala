from django.urls import path
from . import views

app_name = 'monitoring'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('host/<str:host_id>/', views.host_detail, name='host_detail'),
    path('host/<str:host_id>/topic/<path:topic_name>/fields/', views.topic_field_selection, name='topic_field_selection'),
    path('host/<str:host_id>/topic/<path:topic_name>/field/<str:field_name>/', views.topic_chart, name='topic_chart'),
    path('api/host/<str:host_id>/topic/<path:topic_name>/field/<str:field_name>/data/', views.api_chart_data, name='api_chart_data'),
    path('export/host/<str:host_id>/topic/<path:topic_name>/field/<str:field_name>/', views.export_csv, name='export_csv'),
]
