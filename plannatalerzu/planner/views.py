from itertools import groupby

from django.shortcuts import redirect, render

from recipes.models import Recipe

from .models import DAY_CHOICES, MealPlan


DAYS = [choice[1] for choice in DAY_CHOICES]


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
    entries = MealPlan.objects.order_by("name")
    order_map = {day: index for index, day in enumerate(DAYS)}
    planners = []
    for name, group in groupby(entries, key=lambda entry: entry.name):
        rows = sorted(list(group), key=lambda item: order_map.get(item.day_of_week, 0))
        planners.append({"name": name, "rows": rows, "edit_mode": name == edit_plan_name})

    return render(
        request,
        "planner/index.html",
        {"page_title": "Planowanie", "planners": planners, "recipes": Recipe.objects.order_by("name")},
    )
