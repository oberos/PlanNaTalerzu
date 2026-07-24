from itertools import groupby

from django.shortcuts import redirect, render
from recipes.models import Recipe

from .models import DAY_CHOICES, MealPlan

DAYS = [choice[1] for choice in DAY_CHOICES]


def _get_calories_per_serving(recipe):
    """Zwraca kalorie na porcję dla przepisu lub 0 jeśli brak danych."""
    if recipe is None:
        return 0
    nutrition = recipe.calculate_nutrition()
    if nutrition["total"]["has_nutrition_data"]:
        return float(nutrition["per_serving"]["calories"])
    return 0


def planner_index(request):
    if request.method == "POST":
        action = request.POST.get("action")
        if action == "create":
            name = request.POST.get("name", "").strip()
            if name:
                for _, day_name in DAY_CHOICES:
                    MealPlan.objects.create(
                        name=name,
                        day_of_week=day_name,
                        recipe_dinner=None,
                        recipe_dinner_alternative=None,
                        recipe_supper=None,
                    )
        elif action == "delete":
            plan_name = request.POST.get("plan_name")
            if plan_name:
                MealPlan.objects.filter(name=plan_name).delete()
        elif action == "update":
            plan_name = request.POST.get("planner_name", "").strip()
            if plan_name:
                for row in MealPlan.objects.filter(name=plan_name):
                    for field_name in ("recipe_dinner", "recipe_dinner_alternative", "recipe_supper"):
                        field_key = f"{field_name}_{row.pk}"
                        raw_value = request.POST.get(field_key, "")
                        if raw_value:
                            recipe = Recipe.objects.filter(pk=raw_value).first()
                            setattr(row, field_name, recipe)
                        else:
                            setattr(row, field_name, None)
                    row.save()
        return redirect("planner:index")

    edit_plan_name = request.GET.get("edit_plan", "").strip()
    entries = (
        MealPlan.objects.select_related("recipe_dinner", "recipe_dinner_alternative", "recipe_supper")
        .prefetch_related(
            "recipe_dinner__ingredients__ingredient__nutrition",
            "recipe_dinner_alternative__ingredients__ingredient__nutrition",
            "recipe_supper__ingredients__ingredient__nutrition",
        )
        .order_by("name")
    )
    order_map = {day: index for index, day in enumerate(DAYS)}
    planners = []
    for name, group in groupby(entries, key=lambda entry: entry.name):
        rows = sorted(list(group), key=lambda item: order_map.get(item.day_of_week, 0))
        # Dodaj informacje o kaloriach do każdego wiersza
        for row in rows:
            dinner_cal = _get_calories_per_serving(row.recipe_dinner)
            supper_cal = _get_calories_per_serving(row.recipe_supper)
            alt_cal = _get_calories_per_serving(row.recipe_dinner_alternative)

            row.calories_main = dinner_cal + supper_cal  # Obiad + Kolacja
            row.calories_alt = alt_cal + supper_cal  # Alternatywa + Kolacja
        planners.append({"name": name, "rows": rows, "edit_mode": name == edit_plan_name})

    return render(
        request,
        "planner/index.html",
        {"page_title": "Planowanie", "planners": planners, "recipes": Recipe.objects.order_by("name")},
    )
