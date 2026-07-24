from django.contrib import admin

from .models import Ingredient, Recipe, RecipeIngredient


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "preparation_time", "servings")
    search_fields = ("name", "category")


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "default_unit")
    search_fields = ("name", "category")


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ("recipe", "ingredient", "amount", "unit")
    search_fields = ("recipe__name", "ingredient__name")
