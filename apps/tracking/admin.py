from django.contrib import admin
from .models import DailyLog, FoodEntry


class FoodEntryInline(admin.TabularInline):
    model = FoodEntry
    extra = 0
    raw_id_fields = ['food']


@admin.register(DailyLog)
class DailyLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'date']
    list_filter = ['user', 'date']
    inlines = [FoodEntryInline]
