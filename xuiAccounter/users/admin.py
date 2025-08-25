from django.contrib import admin
from .models import UserMetaData

@admin.register(UserMetaData)
class UserMetaDataAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'email')
    search_fields = ('user__username', 'email')
    ordering = ('user__username',)