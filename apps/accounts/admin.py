from django.contrib import admin
from .models import UserProfile, IMTRecord


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'gender', 'activity_level', 'birth_date']


@admin.register(IMTRecord)
class IMTRecordAdmin(admin.ModelAdmin):
    list_display = ['user', 'weight_kg', 'height_cm', 'recorded_at']
    list_filter = ['user']
