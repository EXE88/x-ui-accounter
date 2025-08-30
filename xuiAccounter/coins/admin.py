from django.contrib import admin
from .models import Coin

@admin.register(Coin)
class CoinAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "number_of_coins") 
    list_filter = ("user",)
    search_fields = ("user__username",)
    ordering = ("-number_of_coins",)
