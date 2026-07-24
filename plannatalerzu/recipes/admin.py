from django.contrib import admin

from .models import Ingredient, NutritionInfo, Recipe, RecipeIngredient


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "preparation_time", "servings")
    search_fields = ("name", "category")


class NutritionInfoInline(admin.StackedInline):
    """Inline do edycji wartości odżywczych przy składniku."""

    model = NutritionInfo
    can_delete = False
    verbose_name = "wartości odżywcze"
    verbose_name_plural = "wartości odżywcze"


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "default_unit", "has_nutrition")
    search_fields = ("name", "category")
    inlines = [NutritionInfoInline]

    @admin.display(boolean=True, description="Wartości odżywcze")
    def has_nutrition(self, obj):
        return hasattr(obj, "nutrition")


@admin.register(NutritionInfo)
class NutritionInfoAdmin(admin.ModelAdmin):
    list_display = ("ingredient", "calories", "protein", "carbohydrates", "fat", "fiber")
    search_fields = ("ingredient__name",)
    list_filter = ("ingredient__category",)
    ordering = ("ingredient__name",)


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ("recipe", "ingredient", "amount", "unit")
    search_fields = ("recipe__name", "ingredient__name")
