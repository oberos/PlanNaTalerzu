from decimal import Decimal, InvalidOperation
from itertools import zip_longest

from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

from .models import Ingredient, Recipe, RecipeIngredient


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
    new_ingredient_amounts = request.POST.getlist("new_ingredient_amount")
    new_ingredient_units = request.POST.getlist("new_ingredient_unit")

    rows = zip_longest(
        ingredient_ids,
        ingredient_amounts,
        ingredient_units,
        new_ingredient_names,
        new_ingredient_amounts,
        new_ingredient_units,
        fillvalue="",
    )

    for ingredient_id, amount, unit, new_name, new_amount, new_unit in rows:
        if ingredient_id:
            _add_recipe_ingredient(
                recipe,
                ingredient_id=ingredient_id,
                amount=amount,
                unit=unit,
            )

        if new_name:
            _add_recipe_ingredient(
                recipe,
                ingredient_name=new_name,
                amount=new_amount,
                unit=new_unit,
            )

    for name in _parse_new_ingredients(request.POST.get("new_ingredients", "")):
        _add_recipe_ingredient(recipe, ingredient_name=name)


def recipe_index(request):
    recipes = Recipe.objects.prefetch_related("ingredients__ingredient").all()
    ingredients = Ingredient.objects.order_by("name").all()
    editing_recipe = None

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "delete":
            recipe = get_object_or_404(Recipe, pk=request.POST.get("recipe_id"))
            recipe.delete()
            return redirect("recipes:index")

        with transaction.atomic():
            if action == "create":
                recipe = Recipe.objects.create(
                    name=request.POST.get("name", "").strip(),
                    description=request.POST.get("description", "").strip(),
                    preparation_time=int(request.POST.get("preparation_time") or 0),
                    servings=int(request.POST.get("servings") or 1),
                    category=request.POST.get("category", "").strip(),
                )
            elif action == "update":
                recipe = get_object_or_404(Recipe, pk=request.POST.get("recipe_id"))
                recipe.name = request.POST.get("name", "").strip()
                recipe.description = request.POST.get("description", "").strip()
                recipe.preparation_time = int(request.POST.get("preparation_time") or 0)
                recipe.servings = int(request.POST.get("servings") or 1)
                recipe.category = request.POST.get("category", "").strip()
                recipe.save()
            else:
                recipe = None

            if recipe is not None:
                _add_recipe_ingredients_from_post(recipe, request)

        return redirect("recipes:index")

    edit_id = request.GET.get("edit")
    if edit_id:
        editing_recipe = get_object_or_404(Recipe, pk=edit_id)

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
