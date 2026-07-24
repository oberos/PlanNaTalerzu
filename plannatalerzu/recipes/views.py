from decimal import Decimal, InvalidOperation
from itertools import zip_longest

from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from .import_utils import (
    ParsedRecipe,
    parse_recipe_from_markdown,
    parse_recipe_from_url,
    validate_parsed_recipe,
)
from .models import Ingredient, NutritionInfo, Recipe, RecipeIngredient


def _parse_new_ingredients(raw_value):
    if not raw_value:
        return []

    parts = raw_value.replace("\n", ",").split(",")
    return [part.strip() for part in parts if part.strip()]


def _parse_amount(raw_value):
    if raw_value in (None, ""):
        return Decimal("0")

    try:
        return Decimal(str(raw_value).replace(",", "."))
    except InvalidOperation:
        return Decimal("0")


def _add_recipe_ingredient(recipe, ingredient=None, ingredient_name=None, ingredient_id=None, amount="", unit=""):
    if ingredient is None:
        if ingredient_id:
            ingredient = Ingredient.objects.filter(pk=ingredient_id).first()
        elif ingredient_name:
            ingredient = Ingredient.objects.filter(name__iexact=ingredient_name).first()

    if ingredient is None and ingredient_name:
        ingredient = Ingredient.objects.create(name=ingredient_name, default_unit=unit or "")

    if ingredient is None:
        return

    if unit and ingredient.default_unit != unit:
        ingredient.default_unit = unit
        ingredient.save(update_fields=["default_unit"])

    RecipeIngredient.objects.update_or_create(
        recipe=recipe,
        ingredient=ingredient,
        defaults={"amount": _parse_amount(amount), "unit": unit},
    )


def _add_recipe_ingredients_from_post(recipe, request):
    ingredient_ids = request.POST.getlist("ingredient_id")
    ingredient_amounts = request.POST.getlist("ingredient_amount")
    ingredient_units = request.POST.getlist("ingredient_unit")
    new_ingredient_names = request.POST.getlist("new_ingredient_name")

    rows = zip_longest(
        ingredient_ids,
        ingredient_amounts,
        ingredient_units,
        new_ingredient_names,
        fillvalue="",
    )

    for ingredient_id, amount, unit, new_name in rows:
        if ingredient_id:
            _add_recipe_ingredient(
                recipe,
                ingredient_id=ingredient_id,
                amount=amount,
                unit=unit,
            )
        elif new_name:
            # Use same amount/unit fields for new ingredient (shared row)
            _add_recipe_ingredient(
                recipe,
                ingredient_name=new_name,
                amount=amount,
                unit=unit,
            )

    for name in _parse_new_ingredients(request.POST.get("new_ingredients", "")):
        _add_recipe_ingredient(recipe, ingredient_name=name)


def recipe_index(request):
    recipes = Recipe.objects.prefetch_related("ingredients__ingredient").all()
    ingredients = Ingredient.objects.order_by("name").all()
    editing_recipe = None

    if request.method == "POST":
        action = request.POST.get("action")

        # AJAX: Tworzenie nowego składnika
        if action == "create_ingredient":
            name = request.POST.get("name", "").strip()
            category = request.POST.get("category", "").strip()

            if not name:
                return JsonResponse({"success": False, "error": "Nazwa składnika jest wymagana."})

            # Sprawdź czy składnik już istnieje
            existing = Ingredient.objects.filter(name__iexact=name).first()
            if existing:
                return JsonResponse(
                    {
                        "success": True,
                        "id": existing.pk,
                        "name": existing.name,
                        "default_unit": existing.default_unit or "g",
                        "message": "Składnik już istnieje.",
                    }
                )

            ingredient = Ingredient.objects.create(name=name, category=category, default_unit="g")

            # Dodaj wartości odżywcze jeśli podano
            calories = request.POST.get("calories", "").strip()
            protein = request.POST.get("protein", "").strip()
            carbohydrates = request.POST.get("carbohydrates", "").strip()
            fat = request.POST.get("fat", "").strip()
            fiber = request.POST.get("fiber", "").strip()

            if any([calories, protein, carbohydrates, fat, fiber]):
                NutritionInfo.objects.create(
                    ingredient=ingredient,
                    calories=Decimal(calories) if calories else Decimal("0"),
                    protein=Decimal(protein) if protein else Decimal("0"),
                    carbohydrates=Decimal(carbohydrates) if carbohydrates else Decimal("0"),
                    fat=Decimal(fat) if fat else Decimal("0"),
                    fiber=Decimal(fiber) if fiber else Decimal("0"),
                )

            return JsonResponse(
                {"success": True, "id": ingredient.pk, "name": ingredient.name, "default_unit": ingredient.default_unit}
            )

        if action == "delete":
            recipe = get_object_or_404(Recipe, pk=request.POST.get("recipe_id"))
            recipe.delete()
            return redirect("recipes:index")

        with transaction.atomic():
            if action == "create":
                recipe = Recipe.objects.create(
                    name=request.POST.get("name", "").strip(),
                    description=request.POST.get("description", "").strip(),
                    instructions=request.POST.get("instructions", "").strip(),
                    preparation_time=int(request.POST.get("preparation_time") or 0),
                    servings=int(request.POST.get("servings") or 1),
                    category=request.POST.get("category", "").strip(),
                )
            elif action == "update":
                recipe = get_object_or_404(Recipe, pk=request.POST.get("recipe_id"))
                recipe.name = request.POST.get("name", "").strip()
                recipe.description = request.POST.get("description", "").strip()
                recipe.instructions = request.POST.get("instructions", "").strip()
                recipe.preparation_time = int(request.POST.get("preparation_time") or 0)
                recipe.servings = int(request.POST.get("servings") or 1)
                recipe.category = request.POST.get("category", "").strip()
                recipe.save()
                # Usuń stare składniki przed dodaniem nowych
                recipe.ingredients.all().delete()
            else:
                recipe = None

            if recipe is not None:
                _add_recipe_ingredients_from_post(recipe, request)

        return redirect("recipes:index")

    edit_id = request.GET.get("edit")
    if edit_id:
        editing_recipe = Recipe.objects.prefetch_related("ingredients__ingredient").get(pk=edit_id)

    return render(
        request,
        "recipes/index.html",
        {
            "page_title": "Przepisy",
            "recipes": recipes,
            "ingredients": ingredients,
            "editing_recipe": editing_recipe,
        },
    )


def _create_recipe_from_parsed(parsed: ParsedRecipe) -> Recipe:
    """Tworzy przepis w bazie danych na podstawie sparsowanych danych."""
    with transaction.atomic():
        recipe = Recipe.objects.create(
            name=parsed.name,
            description=parsed.description,
            instructions=parsed.instructions,
            preparation_time=parsed.preparation_time,
            servings=parsed.servings,
            category=parsed.category,
        )

        for ing in parsed.ingredients:
            if not ing.name:
                continue

            # Znajdź lub utwórz składnik
            ingredient, _ = Ingredient.objects.get_or_create(
                name__iexact=ing.name,
                defaults={"name": ing.name, "default_unit": ing.unit or "g"},
            )

            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=ingredient,
                amount=Decimal(str(ing.amount)),
                unit=ing.unit,
            )

    return recipe


def import_preview(request):
    """Podgląd przepisu przed importem (AJAX)."""
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "Wymagane żądanie POST"})

    import_type = request.POST.get("type", "")
    content = request.POST.get("content", "").strip()

    if not content:
        return JsonResponse({"success": False, "error": "Brak danych do importu"})

    try:
        if import_type == "url":
            parsed = parse_recipe_from_url(content)
        elif import_type == "markdown":
            parsed = parse_recipe_from_markdown(content)
        else:
            return JsonResponse({"success": False, "error": "Nieznany typ importu"})

        warnings = validate_parsed_recipe(parsed)

        return JsonResponse(
            {
                "success": True,
                "recipe": {
                    "name": parsed.name,
                    "description": parsed.description,
                    "instructions": parsed.instructions,
                    "preparation_time": parsed.preparation_time,
                    "servings": parsed.servings,
                    "category": parsed.category,
                    "ingredients": [
                        {"name": ing.name, "amount": ing.amount, "unit": ing.unit} for ing in parsed.ingredients
                    ],
                    "source_url": parsed.source_url,
                },
                "warnings": warnings,
            }
        )
    except ValueError as e:
        return JsonResponse({"success": False, "error": str(e)})
    except Exception as e:
        return JsonResponse({"success": False, "error": f"Błąd podczas parsowania: {e}"})


def import_confirm(request):
    """Potwierdza import przepisu i zapisuje do bazy (AJAX)."""
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "Wymagane żądanie POST"})

    import_type = request.POST.get("type", "")
    content = request.POST.get("content", "").strip()

    if not content:
        return JsonResponse({"success": False, "error": "Brak danych do importu"})

    try:
        if import_type == "url":
            parsed = parse_recipe_from_url(content)
        elif import_type == "markdown":
            parsed = parse_recipe_from_markdown(content)
        else:
            return JsonResponse({"success": False, "error": "Nieznany typ importu"})

        # Sprawdź czy przepis o takiej nazwie już istnieje
        if Recipe.objects.filter(name__iexact=parsed.name).exists():
            return JsonResponse(
                {
                    "success": False,
                    "error": f"Przepis o nazwie '{parsed.name}' już istnieje",
                }
            )

        recipe = _create_recipe_from_parsed(parsed)

        return JsonResponse(
            {
                "success": True,
                "message": f"Przepis '{recipe.name}' został zaimportowany",
                "recipe_id": recipe.pk,
            }
        )
    except ValueError as e:
        return JsonResponse({"success": False, "error": str(e)})
    except Exception as e:
        return JsonResponse({"success": False, "error": f"Błąd podczas importu: {e}"})


def ingredient_index(request):
    """Widok zarządzania składnikami."""
    ingredients = Ingredient.objects.select_related("nutrition").order_by("name").all()
    editing_ingredient = None

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "delete":
            ingredient = get_object_or_404(Ingredient, pk=request.POST.get("ingredient_id"))
            ingredient.delete()
            return redirect("recipes:ingredients")

        if action == "create":
            name = request.POST.get("name", "").strip()
            if not name:
                return redirect("recipes:ingredients")

            # Sprawdź czy składnik już istnieje
            if Ingredient.objects.filter(name__iexact=name).exists():
                return redirect("recipes:ingredients")

            ingredient = Ingredient.objects.create(
                name=name,
                category=request.POST.get("category", "").strip(),
                default_unit=request.POST.get("default_unit", "g").strip(),
            )
            _update_nutrition_from_post(ingredient, request)
            return redirect("recipes:ingredients")

        if action == "update":
            ingredient = get_object_or_404(Ingredient, pk=request.POST.get("ingredient_id"))
            ingredient.name = request.POST.get("name", "").strip()
            ingredient.category = request.POST.get("category", "").strip()
            ingredient.default_unit = request.POST.get("default_unit", "g").strip()
            ingredient.save()
            _update_nutrition_from_post(ingredient, request)
            return redirect("recipes:ingredients")

    edit_id = request.GET.get("edit")
    if edit_id:
        editing_ingredient = Ingredient.objects.select_related("nutrition").get(pk=edit_id)

    return render(
        request,
        "recipes/ingredients.html",
        {
            "page_title": "Składniki",
            "ingredients": ingredients,
            "editing_ingredient": editing_ingredient,
        },
    )


def _update_nutrition_from_post(ingredient, request):
    """Aktualizuje lub tworzy wartości odżywcze dla składnika na podstawie POST."""
    calories = request.POST.get("calories", "").strip()
    protein = request.POST.get("protein", "").strip()
    carbohydrates = request.POST.get("carbohydrates", "").strip()
    fat = request.POST.get("fat", "").strip()
    fiber = request.POST.get("fiber", "").strip()

    # Jeśli podano jakiekolwiek wartości, utwórz/zaktualizuj NutritionInfo
    if any([calories, protein, carbohydrates, fat, fiber]):
        nutrition, _ = NutritionInfo.objects.get_or_create(ingredient=ingredient)
        nutrition.calories = Decimal(calories) if calories else Decimal("0")
        nutrition.protein = Decimal(protein) if protein else Decimal("0")
        nutrition.carbohydrates = Decimal(carbohydrates) if carbohydrates else Decimal("0")
        nutrition.fat = Decimal(fat) if fat else Decimal("0")
        nutrition.fiber = Decimal(fiber) if fiber else Decimal("0")
        nutrition.save()
    else:
        # Jeśli wszystkie wartości są puste, usuń NutritionInfo jeśli istnieje
        try:
            ingredient.nutrition.delete()
        except NutritionInfo.DoesNotExist:
            pass
