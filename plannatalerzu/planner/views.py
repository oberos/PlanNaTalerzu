from itertools import groupby
import json
from decimal import Decimal

from django.shortcuts import redirect, render
from django.http import JsonResponse, HttpResponseBadRequest
from recipes.models import Recipe, Ingredient

from .models import DAY_CHOICES, MealPlan, MealItem

DAYS = [choice[1] for choice in DAY_CHOICES]


def _get_calories_per_serving(recipe):
    """Zwraca kalorie na porcję dla przepisu lub 0 jeśli brak danych."""
    if recipe is None:
        return 0
    nutrition = recipe.calculate_nutrition()
    if nutrition["total"]["has_nutrition_data"]:
        return float(nutrition["per_serving"]["calories"])
    return 0


def _get_macros_per_serving(recipe):
    """Zwraca makroskładniki (protein, carbs, fat) na porcję jako słownik lub zera."""
    if recipe is None:
        return {"protein": 0, "carbohydrates": 0, "fat": 0}
    nutrition = recipe.calculate_nutrition()
    if nutrition["total"]["has_nutrition_data"]:
        return {
            "protein": float(nutrition["per_serving"]["protein"]),
            "carbohydrates": float(nutrition["per_serving"]["carbohydrates"]),
            "fat": float(nutrition["per_serving"]["fat"]),
        }
    return {"protein": 0, "carbohydrates": 0, "fat": 0}


def planner_index(request):
    if request.method == "POST":
        action = request.POST.get("action")
        if action == "delete_item":
            item_id = request.POST.get("item_id")
            if not item_id:
                return HttpResponseBadRequest("missing item_id")
            item = MealItem.objects.filter(pk=item_id).first()
            if not item:
                return HttpResponseBadRequest("item not found")
            item.delete()
            return JsonResponse({"status": "ok"})
        # Ajax endpoint: add a single MealItem immediately
        if action == "add_item":
            plan_name = request.POST.get("planner_name", "").strip()
            row_pk = request.POST.get("row")
            meal = request.POST.get("meal")
            payload_raw = request.POST.get("payload")
            try:
                payload = json.loads(payload_raw or "{}")
            except Exception:
                return HttpResponseBadRequest("invalid payload")

            if not plan_name or not row_pk or not meal:
                return HttpResponseBadRequest("missing parameters")

            row = MealPlan.objects.filter(name=plan_name, pk=row_pk).first()
            if not row:
                return HttpResponseBadRequest("row not found")

            # helper mapping for unit -> grams (same assumptions as Recipe.calculate_nutrition)
            unit_to_grams = {
                "g": Decimal("1"),
                "kg": Decimal("1000"),
                "dag": Decimal("10"),
                "mg": Decimal("0.001"),
                "ml": Decimal("1"),
                "l": Decimal("1000"),
                "łyżka": Decimal("15"),
                "łyżeczka": Decimal("5"),
                "szklanka": Decimal("250"),
                "szczypta": Decimal("0.5"),
                "szt": Decimal("100"),
            }

            # create item and compute simple nutrition info to return
            if payload.get("type") == "recipe":
                recipe = None
                if payload.get("id"):
                    recipe = Recipe.objects.filter(pk=payload.get("id")).first()
                item = MealItem.objects.create(mealplan=row, meal=meal, type="recipe", recipe=recipe)

                # compute nutrition: use per_serving values and scale by requested servings (if provided)
                cal = 0.0
                prot = 0.0
                carbs = 0.0
                fat = 0.0
                servings_used = 1
                try:
                    if payload.get("servings"):
                        s = str(payload.get("servings")).strip()
                        if s != "":
                            servings_used = int(s)
                except Exception:
                    servings_used = 1
                if recipe:
                    nutrition = recipe.calculate_nutrition()
                    if nutrition and nutrition["total"]["has_nutrition_data"]:
                        per = nutrition.get("per_serving", {})
                        cal = float(per.get("calories", 0) or 0) * servings_used
                        prot = float(per.get("protein", 0) or 0) * servings_used
                        carbs = float(per.get("carbohydrates", 0) or 0) * servings_used
                        fat = float(per.get("fat", 0) or 0) * servings_used

                # persist nutrition snapshot on the item
                try:
                    item.calories = cal
                    item.protein = prot
                    item.carbohydrates = carbs
                    item.fat = fat
                    item.save()
                except Exception:
                    pass

                return JsonResponse(
                    {
                        "status": "ok",
                        "id": item.pk,
                        "type": "recipe",
                        "name": recipe.name if recipe else payload.get("name"),
                        "nutrition": {
                            "calories": round(float(item.calories), 1),
                            "protein": round(float(item.protein), 1),
                            "carbohydrates": round(float(item.carbohydrates), 1),
                            "fat": round(float(item.fat), 1),
                        },
                    }
                )
            else:
                name = payload.get("name") or ""
                amount = payload.get("amount")
                unit = (payload.get("unit") or "").lower().strip()
                dec_amount = None
                try:
                    if amount not in (None, ""):
                        dec_amount = Decimal(str(amount))
                except Exception:
                    dec_amount = None

                item = MealItem.objects.create(
                    mealplan=row,
                    meal=meal,
                    type="ingredient",
                    ingredient_name=name,
                    ingredient_amount=dec_amount,
                    ingredient_unit=unit,
                )

                # compute nutrition from ingredient.nutrition if available
                cal = 0.0
                prot = 0.0
                carbs = 0.0
                fat = 0.0
                if payload.get("id"):
                    ing = Ingredient.objects.filter(pk=payload.get("id")).first()
                    if ing:
                        try:
                            nut = ing.nutrition
                        except Exception:
                            nut = None
                        if nut and dec_amount is not None:
                            conv = unit_to_grams.get(unit, Decimal("1"))
                            amount_in_grams = dec_amount * conv
                            multiplier = amount_in_grams / Decimal("100")
                            try:
                                cal = float(round(nut.calories * multiplier, 1))
                                prot = float(round(nut.protein * multiplier, 1))
                                carbs = float(round(nut.carbohydrates * multiplier, 1))
                                fat = float(round(nut.fat * multiplier, 1))
                            except Exception:
                                cal = prot = carbs = fat = 0.0

                # persist nutrition snapshot
                try:
                    item.calories = cal
                    item.protein = prot
                    item.carbohydrates = carbs
                    item.fat = fat
                    item.save()
                except Exception:
                    pass

                return JsonResponse(
                    {
                        "status": "ok",
                        "id": item.pk,
                        "type": "ingredient",
                        "name": name,
                        "amount": str(dec_amount) if dec_amount is not None else None,
                        "unit": unit,
                        "nutrition": {
                            "calories": round(float(item.calories), 1),
                            "protein": round(float(item.protein), 1),
                            "carbohydrates": round(float(item.carbohydrates), 1),
                            "fat": round(float(item.fat), 1),
                        },
                    }
                )
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
                    for field_name in (
                        "recipe_breakfast",
                        "recipe_second_breakfast",
                        "recipe_dinner",
                        "recipe_dinner_alternative",
                        "recipe_supper",
                    ):
                        field_key = f"{field_name}_{row.pk}"
                        raw_value = request.POST.get(field_key, "")
                        if raw_value:
                            recipe = Recipe.objects.filter(pk=raw_value).first()
                            setattr(row, field_name, recipe)
                        else:
                            setattr(row, field_name, None)
                    row.save()
                    # process any new_item_* hidden inputs for this row
                    for meal in ("dinner", "supper", "alternative"):
                        key = f"new_item_{plan_name}_{row.pk}_{meal}[]"
                        values = request.POST.getlist(key)
                        for val in values:
                            try:
                                payload = json.loads(val)
                            except Exception:
                                continue
                            if not isinstance(payload, dict):
                                continue
                            if payload.get("type") == "recipe":
                                recipe = None
                                if payload.get("id"):
                                    recipe = Recipe.objects.filter(pk=payload.get("id")).first()
                                mi = MealItem.objects.create(mealplan=row, meal=meal, type="recipe", recipe=recipe)
                                # compute and persist nutrition snapshot
                                try:
                                    cal = prot = carbs = fat = 0.0
                                    servings_used = 1
                                    if payload.get("servings"):
                                        try:
                                            s = str(payload.get("servings")).strip()
                                            if s != "":
                                                servings_used = int(s)
                                        except Exception:
                                            servings_used = 1
                                    if recipe:
                                        nutr = recipe.calculate_nutrition()
                                        if nutr and nutr["total"]["has_nutrition_data"]:
                                            per = nutr.get("per_serving", {})
                                            cal = float(per.get("calories", 0) or 0) * servings_used
                                            prot = float(per.get("protein", 0) or 0) * servings_used
                                            carbs = float(per.get("carbohydrates", 0) or 0) * servings_used
                                            fat = float(per.get("fat", 0) or 0) * servings_used
                                    mi.calories = cal
                                    mi.protein = prot
                                    mi.carbohydrates = carbs
                                    mi.fat = fat
                                    mi.save()
                                except Exception:
                                    pass
                            else:
                                name = payload.get("name") or ""
                                amount = payload.get("amount")
                                unit = payload.get("unit") or ""
                                dec_amount = None
                                try:
                                    if amount not in (None, ""):
                                        dec_amount = Decimal(str(amount))
                                except Exception:
                                    dec_amount = None
                                mi = MealItem.objects.create(
                                    mealplan=row,
                                    meal=meal,
                                    type="ingredient",
                                    ingredient_name=name,
                                    ingredient_amount=dec_amount,
                                    ingredient_unit=unit,
                                )
                                # compute and persist ingredient nutrition where possible
                                try:
                                    cal = prot = carbs = fat = 0.0
                                    if payload.get("id"):
                                        ing = Ingredient.objects.filter(pk=payload.get("id")).first()
                                        if ing and hasattr(ing, "nutrition") and dec_amount is not None:
                                            unit_to_grams = {
                                                "g": Decimal("1"),
                                                "kg": Decimal("1000"),
                                                "dag": Decimal("10"),
                                                "mg": Decimal("0.001"),
                                                "ml": Decimal("1"),
                                                "l": Decimal("1000"),
                                                "łyżka": Decimal("15"),
                                                "łyżeczka": Decimal("5"),
                                                "szklanka": Decimal("250"),
                                                "szczypta": Decimal("0.5"),
                                                "szt": Decimal("100"),
                                            }
                                            conv = unit_to_grams.get((unit or "").lower().strip(), Decimal("1"))
                                            amount_in_grams = dec_amount * conv
                                            multiplier = amount_in_grams / Decimal("100")
                                            try:
                                                nut = ing.nutrition
                                                cal = float(round(nut.calories * multiplier, 1))
                                                prot = float(round(nut.protein * multiplier, 1))
                                                carbs = float(round(nut.carbohydrates * multiplier, 1))
                                                fat = float(round(nut.fat * multiplier, 1))
                                            except Exception:
                                                cal = prot = carbs = fat = 0.0
                                    mi.calories = cal
                                    mi.protein = prot
                                    mi.carbohydrates = carbs
                                    mi.fat = fat
                                    mi.save()
                                except Exception:
                                    pass
        return redirect("planner:index")

    edit_plan_name = request.GET.get("edit_plan", "").strip()
    entries = (
        MealPlan.objects.select_related("recipe_dinner", "recipe_dinner_alternative", "recipe_supper")
        .prefetch_related(
            "recipe_breakfast__ingredients__ingredient__nutrition",
            "recipe_second_breakfast__ingredients__ingredient__nutrition",
            "recipe_dinner__ingredients__ingredient__nutrition",
            "recipe_dinner_alternative__ingredients__ingredient__nutrition",
            "recipe_supper__ingredients__ingredient__nutrition",
            "items",
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
            row.calories_alt = alt_cal + supper_cal  # Obiad + Kolacja
            # Makroskładniki
            dinner_mac = _get_macros_per_serving(row.recipe_dinner)
            supper_mac = _get_macros_per_serving(row.recipe_supper)
            alt_mac = _get_macros_per_serving(row.recipe_dinner_alternative)

            row.protein_main = round(dinner_mac["protein"] + supper_mac["protein"], 1)
            row.carbs_main = round(dinner_mac["carbohydrates"] + supper_mac["carbohydrates"], 1)
            row.fat_main = round(dinner_mac["fat"] + supper_mac["fat"], 1)

            row.protein_alt = round(alt_mac["protein"] + supper_mac["protein"], 1)
            row.carbs_alt = round(alt_mac["carbohydrates"] + supper_mac["carbohydrates"], 1)
            row.fat_alt = round(alt_mac["fat"] + supper_mac["fat"], 1)
            # attach existing meal items grouped by meal
            items = list(getattr(row, "items").all()) if hasattr(row, "items") else []
            # compute per-item nutrition where possible
            for it in items:
                # prefer persisted nutrition snapshot if available
                try:
                    c = float(it.calories or 0)
                    p = float(it.protein or 0)
                    w = float(it.carbohydrates or 0)
                    f = float(it.fat or 0)
                    it.nutrition = {
                        "calories": round(c, 1),
                        "protein": round(p, 1),
                        "carbohydrates": round(w, 1),
                        "fat": round(f, 1),
                    }
                    # if all zeros, attempt to compute from recipe/ingredient as fallback
                    if c == 0 and p == 0 and w == 0 and f == 0:
                        raise ValueError("no persisted nutrition")
                except Exception:
                    it.nutrition = {"calories": 0.0, "protein": 0.0, "carbohydrates": 0.0, "fat": 0.0}
                    try:
                        if it.type == "recipe" and it.recipe:
                            nutr = it.recipe.calculate_nutrition()
                            if nutr and nutr["total"]["has_nutrition_data"]:
                                per = nutr.get("per_serving", {})
                                it.nutrition = {
                                    "calories": float(per.get("calories", 0) or 0),
                                    "protein": float(per.get("protein", 0) or 0),
                                    "carbohydrates": float(per.get("carbohydrates", 0) or 0),
                                    "fat": float(per.get("fat", 0) or 0),
                                }
                        elif it.type == "ingredient" and it.ingredient_name:
                            # try to find matching Ingredient by name
                            ing = Ingredient.objects.filter(name__iexact=it.ingredient_name).first()
                            if ing and hasattr(ing, "nutrition") and it.ingredient_amount:
                                # convert unit to grams using same assumptions as Recipe.calculate_nutrition
                                unit_to_grams = {
                                    "g": Decimal("1"),
                                    "kg": Decimal("1000"),
                                    "dag": Decimal("10"),
                                    "mg": Decimal("0.001"),
                                    "ml": Decimal("1"),
                                    "l": Decimal("1000"),
                                    "łyżka": Decimal("15"),
                                    "łyżeczka": Decimal("5"),
                                    "szklanka": Decimal("250"),
                                    "szczypta": Decimal("0.5"),
                                    "szt": Decimal("100"),
                                }
                                unit = (it.ingredient_unit or "").lower().strip()
                                conv = unit_to_grams.get(unit, Decimal("1"))
                                try:
                                    amt = Decimal(it.ingredient_amount)
                                    amount_in_grams = amt * conv
                                    multiplier = amount_in_grams / Decimal("100")
                                    nut = ing.nutrition
                                    it.nutrition = {
                                        "calories": float(round(nut.calories * multiplier, 1)),
                                        "protein": float(round(nut.protein * multiplier, 1)),
                                        "carbohydrates": float(round(nut.carbohydrates * multiplier, 1)),
                                        "fat": float(round(nut.fat * multiplier, 1)),
                                    }
                                except Exception:
                                    pass
                    except Exception:
                        it.nutrition = {"calories": 0.0, "protein": 0.0, "carbohydrates": 0.0, "fat": 0.0}
            row.items_by_meal = {
                "breakfast": [it for it in items if it.meal == "breakfast"],
                "second_breakfast": [it for it in items if it.meal == "second_breakfast"],
                "dinner": [it for it in items if it.meal == "dinner"],
                "supper": [it for it in items if it.meal == "supper"],
                "alternative": [it for it in items if it.meal == "alternative"],
            }
            # compute per-meal totals from persisted item nutrition snapshots
            totals_by_meal = {}
            for meal_name, its in row.items_by_meal.items():
                c = p = cb = f = 0.0
                for it in its:
                    try:
                        c += float(it.calories or 0)
                        p += float(it.protein or 0)
                        cb += float(it.carbohydrates or 0)
                        f += float(it.fat or 0)
                    except Exception:
                        pass
                totals_by_meal[meal_name] = {
                    "calories": round(c, 1),
                    "protein": round(p, 1),
                    "carbohydrates": round(cb, 1),
                    "fat": round(f, 1),
                }
            row.totals_by_meal = totals_by_meal
            # daily totals
            day_c = day_p = day_cb = day_f = 0.0
            for v in totals_by_meal.values():
                day_c += v.get("calories", 0) or 0
                day_p += v.get("protein", 0) or 0
                day_cb += v.get("carbohydrates", 0) or 0
                day_f += v.get("fat", 0) or 0
            row.calories_day = round(day_c, 1)
            row.protein_day = round(day_p, 1)
            row.carbs_day = round(day_cb, 1)
            row.fat_day = round(day_f, 1)
        planners.append({"name": name, "rows": rows, "edit_mode": name == edit_plan_name})

    return render(
        request,
        "planner/index.html",
        {
            "page_title": "Planowanie",
            "planners": planners,
            "recipes": Recipe.objects.order_by("name"),
            "ingredients": Ingredient.objects.order_by("name"),
        },
    )
