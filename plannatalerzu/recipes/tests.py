from django.test import TestCase
from django.urls import reverse

from .models import Ingredient, Recipe, RecipeIngredient


class RecipeModelsTest(TestCase):
    def test_recipe_with_ingredients_can_be_created(self):
        recipe = Recipe.objects.create(
            name="Pasta",
            description="Szybki obiad",
            preparation_time=20,
            servings=4,
            category="dinner",
        )
        ingredient = Ingredient.objects.create(
            name="Pomidor",
            category="warzywa",
            default_unit="g",
        )
        relation = RecipeIngredient.objects.create(
            recipe=recipe,
            ingredient=ingredient,
            amount=200,
            unit="g",
        )

        self.assertEqual(recipe.name, "Pasta")
        self.assertEqual(recipe.ingredients.count(), 1)
        self.assertEqual(relation.amount, 200)


class RecipeViewsTest(TestCase):
    def test_create_recipe_with_existing_and_new_ingredients(self):
        existing_ingredient = Ingredient.objects.create(name="cebula", default_unit="szt")

        response = self.client.post(
            reverse("recipes:index"),
            {
                "action": "create",
                "name": "Kotlet",
                "description": "Smaczny kotlet",
                "preparation_time": 30,
                "servings": 2,
                "category": "dinner",
                "ingredient_id": str(existing_ingredient.pk),
                "ingredient_amount": "2",
                "ingredient_unit": "szt",
                "new_ingredient_name": "marchewka",
                "new_ingredient_amount": "1",
                "new_ingredient_unit": "szt",
            },
        )

        self.assertEqual(response.status_code, 302)
        recipe = Recipe.objects.get(name="Kotlet")
        self.assertTrue(recipe.pk)
        self.assertTrue(Ingredient.objects.filter(name="marchewka").exists())
        relation = RecipeIngredient.objects.get(recipe=recipe, ingredient=existing_ingredient)
        self.assertEqual(relation.amount, 2)
        self.assertEqual(relation.unit, "szt")
        new_relation = RecipeIngredient.objects.get(recipe=recipe, ingredient__name="marchewka")
        self.assertEqual(new_relation.amount, 1)
        self.assertEqual(new_relation.unit, "szt")

    def test_edit_recipe_adds_new_ingredients(self):
        recipe = Recipe.objects.create(
            name="Zupa",
            description="Opis",
            preparation_time=15,
            servings=4,
            category="dinner",
        )
        ingredient = Ingredient.objects.create(name="cebula", default_unit="szt")
        RecipeIngredient.objects.create(recipe=recipe, ingredient=ingredient, amount=1, unit="szt")

        response = self.client.post(
            reverse("recipes:index"),
            {
                "action": "update",
                "recipe_id": recipe.pk,
                "name": "Zupa krem",
                "description": "Nowy opis",
                "preparation_time": 20,
                "servings": 4,
                "category": "soup",
                "new_ingredients": "marchewka",
            },
        )

        self.assertEqual(response.status_code, 302)
        recipe.refresh_from_db()
        self.assertEqual(recipe.name, "Zupa krem")
        self.assertEqual(recipe.category, "soup")
        self.assertTrue(Ingredient.objects.filter(name="marchewka").exists())
        self.assertEqual(RecipeIngredient.objects.filter(recipe=recipe).count(), 2)
