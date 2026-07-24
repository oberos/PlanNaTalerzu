from django.contrib import admin

from .models import MealPlan


@admin.register(MealPlan)
class MealPlanAdmin(admin.ModelAdmin):
    list_display = ("name", "day_of_week", "recipe_dinner", "recipe_supper")
    list_filter = ("name", "day_of_week")
    search_fields = ("name", "recipe_dinner__name", "recipe_dinner_alternative__name", "recipe_supper__name")
