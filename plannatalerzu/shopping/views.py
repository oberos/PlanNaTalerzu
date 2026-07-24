from itertools import groupby

from django.shortcuts import render
from planner.models import MealPlan
from recipes.models import RecipeIngredient

from .unit_converter import aggregate_ingredients


def shopping_index(request):
    """
    Widok listy zakupów.

    GET params:
        plan: nazwa planu do wygenerowania listy
    """
    plan_name = request.GET.get("plan", "").strip()
    available_plans = MealPlan.objects.values_list("name", flat=True).distinct().order_by("name")

    shopping_list = []
    grouped_list = []

    if plan_name:
        # Pobierz wszystkie dni z wybranego planu
        plans = MealPlan.objects.filter(name=plan_name).select_related(
            "recipe_dinner",
            "recipe_dinner_alternative",
            "recipe_supper",
        )

        # Zbierz wszystkie unikalne przepisy
        recipe_ids = set()
        for plan in plans:
            if plan.recipe_dinner_id:
                recipe_ids.add(plan.recipe_dinner_id)
            if plan.recipe_dinner_alternative_id:
                recipe_ids.add(plan.recipe_dinner_alternative_id)
            if plan.recipe_supper_id:
                recipe_ids.add(plan.recipe_supper_id)

        if recipe_ids:
            # Pobierz wszystkie składniki z tych przepisów
            ingredients_data = []
            recipe_ingredients = RecipeIngredient.objects.filter(recipe_id__in=recipe_ids).select_related("ingredient")

            for ri in recipe_ingredients:
                ingredients_data.append(
                    {
                        "ingredient_id": ri.ingredient_id,
                        "ingredient_name": ri.ingredient.name,
                        "ingredient_category": ri.ingredient.category,
                        "amount": ri.amount,
                        "unit": ri.unit,
                    }
                )

            # Agreguj składniki z konwersją jednostek
            shopping_list = aggregate_ingredients(ingredients_data)

            # Grupuj po kategorii
            grouped_list = []
            for category, items in groupby(shopping_list, key=lambda x: x["ingredient_category"] or "Inne"):
                grouped_list.append(
                    {
                        "category": category,
                        "items": list(items),
                    }
                )

    return render(
        request,
        "shopping/index.html",
        {
            "page_title": "Lista zakupów",
            "available_plans": available_plans,
            "selected_plan": plan_name,
            "shopping_list": shopping_list,
            "grouped_list": grouped_list,
        },
    )
