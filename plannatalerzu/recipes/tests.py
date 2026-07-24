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

        # Each row: either existing ingredient OR new ingredient name (not both)
        # Row 1: existing ingredient with amount/unit
        # Row 2: new ingredient with amount/unit
        response = self.client.post(
            reverse("recipes:index"),
            {
                "action": "create",
                "name": "Kotlet",
                "description": "Smaczny kotlet",
                "preparation_time": 30,
                "servings": 2,
                "category": "dinner",
                "ingredient_id": [str(existing_ingredient.pk), ""],
                "ingredient_amount": ["2", "1"],
                "ingredient_unit": ["szt", "szt"],
                "new_ingredient_name": ["", "marchewka"],
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

    def test_edit_recipe_replaces_ingredients(self):
        """Test that editing a recipe replaces all ingredients with new ones from POST."""
        recipe = Recipe.objects.create(
            name="Zupa",
            description="Opis",
            preparation_time=15,
            servings=4,
            category="dinner",
        )
        old_ingredient = Ingredient.objects.create(name="cebula", default_unit="szt")
        new_ingredient = Ingredient.objects.create(name="marchewka", default_unit="g")
        RecipeIngredient.objects.create(recipe=recipe, ingredient=old_ingredient, amount=1, unit="szt")

        # Update recipe with only the new ingredient (old one should be removed)
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
                "ingredient_id": [str(new_ingredient.pk)],
                "ingredient_amount": ["200"],
                "ingredient_unit": ["g"],
            },
        )

        self.assertEqual(response.status_code, 302)
        recipe.refresh_from_db()
        self.assertEqual(recipe.name, "Zupa krem")
        self.assertEqual(recipe.category, "soup")
        # Should have only 1 ingredient (the new one)
        self.assertEqual(RecipeIngredient.objects.filter(recipe=recipe).count(), 1)
        self.assertTrue(RecipeIngredient.objects.filter(recipe=recipe, ingredient=new_ingredient).exists())
        self.assertFalse(RecipeIngredient.objects.filter(recipe=recipe, ingredient=old_ingredient).exists())

    def test_create_ingredient_ajax(self):
        """Test AJAX endpoint for creating new ingredient."""
        response = self.client.post(
            reverse("recipes:index"),
            {
                "action": "create_ingredient",
                "name": "Tofu",
                "category": "białko",
            },
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["name"], "Tofu")
        self.assertTrue(Ingredient.objects.filter(name="Tofu").exists())

    def test_create_ingredient_ajax_duplicate(self):
        """Test AJAX returns existing ingredient if duplicate name."""
        existing = Ingredient.objects.create(name="Cukinia", category="warzywa")

        response = self.client.post(
            reverse("recipes:index"),
            {
                "action": "create_ingredient",
                "name": "cukinia",  # different case
                "category": "inne",
            },
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["id"], existing.pk)
        # Should not create duplicate
        self.assertEqual(Ingredient.objects.filter(name__iexact="cukinia").count(), 1)
