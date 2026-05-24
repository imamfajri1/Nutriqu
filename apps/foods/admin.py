from django.contrib import admin
from .models import Food, NutritionFact


class NutritionFactInline(admin.StackedInline):
    model = NutritionFact
    extra = 0


@admin.register(Food)
class FoodAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'source', 'is_custom']
    search_fields = ['name', 'code']
    list_filter = ['is_custom', 'source']
    inlines = [NutritionFactInline]
