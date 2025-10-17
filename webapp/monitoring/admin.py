from django.contrib import admin
from .models import MqttData


@admin.register(MqttData)
class MqttDataAdmin(admin.ModelAdmin):
    """Admin interface for MqttData model (read-only)."""
    
    list_display = ('host', 'topic', 'time')
    list_filter = ('host', 'topic', 'time')
    search_fields = ('host', 'topic')
    readonly_fields = ('time', 'host', 'topic')
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False