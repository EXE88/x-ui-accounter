from django.contrib import admin
from .models import UserMetaData , EmailVerification
from django.utils.html import format_html
from django.utils import timezone

@admin.register(UserMetaData)
class UserMetaDataAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'email')
    search_fields = ('user__username', 'email')
    ordering = ('user__username',)

@admin.register(EmailVerification)
class EmailVerificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'code', 'created_at', 'is_expired_colored')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'user__email', 'code')
    ordering = ('-created_at',)

    def is_expired_colored(self, obj):
        if obj.is_expired():
            return format_html('<span style="color: red;">Expired ❌</span>')
        return format_html('<span style="color: green;">Valid ✅</span>')

    is_expired_colored.short_description = "status"