from django.contrib import admin
from .models import ConfigCode , GlobalVariables
from datetime import datetime, timedelta

@admin.register(ConfigCode)
class ConfigCodeAdmin(admin.ModelAdmin):
    list_display = ('email', 'user', 'client_id', 'total_gb_display', 'expiry_days', 'created_at')
    
    search_fields = ('email', 'user__username')
    
    list_filter = ('user', 'created_at')
    
    readonly_fields = ('client_id', 'created_at')
    
    ordering = ('-created_at',)
    
    fieldsets = (
        (None, {
            'fields': ('user', 'email', 'total_gb', 'expiry_time')
        }),
        ('Metadata', {
            'fields': ('client_id', 'created_at'),
            'classes': ('collapse',)
        }),
    )
    
    def total_gb_display(self, obj):
        return f"{obj.total_gb / (1024 ** 3):.2f} GB"
    total_gb_display.short_description = 'Total GB'

    def expiry_days(self, obj):
        days_left = obj.expiry_time // (24 * 3600)
        return f"{days_left} days"
    expiry_days.short_description = 'Expiry'

@admin.register(GlobalVariables)
class GlobalVariablesAdmin(admin.ModelAdmin):
    list_display = ('panel_address', 'panel_port', 'panel_username', 'x_ui_listen_port', 'inbound_id')
    
    fieldsets = (
        ('Panel Settings', {
            'fields': ('panel_address', 'panel_port', 'panel_username', 'panel_password')
        }),
        ('X-UI Settings', {
            'fields': ('x_ui_listen_port', 'inbound_id')
        }),
    )

    def has_add_permission(self, request):
        return not GlobalVariables.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        return False
