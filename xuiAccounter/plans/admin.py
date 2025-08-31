from django.contrib import admin
from .models import Plan

@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ('plan_name', 'number_of_users_with_unit', 'time_with_unit', 'usage_with_unit', 'price_with_unit')
    
    search_fields = ('plan_name',)
    list_filter = ('time', 'number_of_users')
    ordering = ('plan_name',)
    list_per_page = 20

    def number_of_users_with_unit(self,obj):
        return f"{obj.number_of_users} کاربره"
    number_of_users_with_unit.short_description = "NUMBER OF USERS"

    def time_with_unit(self, obj):
        return f"{obj.time} ماه"
    time_with_unit.short_description = "TIME (month)"

    def usage_with_unit(self, obj):
        return f"{obj.usage} GB"
    usage_with_unit.short_description = "USAGE (GB)"

    def price_with_unit(self, obj):
        return f"{obj.price} کوین"
    price_with_unit.short_description = "PRICE (Coins)"
