from decimal import Decimal

from django.test import TestCase
from django.urls import reverse
from planner.models import MealPlan
from recipes.models import Ingredient, Recipe, RecipeIngredient

from .unit_converter import aggregate_ingredients, convert_to_base, format_amount


class UnitConverterTest(TestCase):
    """Testy konwersji jednostek."""

    def test_convert_ml_to_base(self):
        result = convert_to_base(Decimal("100"), "ml")
        self.assertEqual(result.amount, Decimal("100"))
        self.assertEqual(result.base_unit, "ml")

    def test_convert_liter_to_ml(self):
        result = convert_to_base(Decimal("1.5"), "l")
        self.assertEqual(result.amount, Decimal("1500"))
        self.assertEqual(result.base_unit, "ml")

    def test_convert_lyżeczka_to_ml(self):
        result = convert_to_base(Decimal("2"), "łyżeczka")
        self.assertEqual(result.amount, Decimal("10"))  # 2 * 5ml
        self.assertEqual(result.base_unit, "ml")

    def test_convert_lyżka_to_ml(self):
        result = convert_to_base(Decimal("3"), "łyżka")
        self.assertEqual(result.amount, Decimal("45"))  # 3 * 15ml
        self.assertEqual(result.base_unit, "ml")

    def test_convert_szklanka_to_ml(self):
        result = convert_to_base(Decimal("2"), "szklanka")
        self.assertEqual(result.amount, Decimal("500"))  # 2 * 250ml
        self.assertEqual(result.base_unit, "ml")

    def test_convert_kg_to_g(self):
        result = convert_to_base(Decimal("0.5"), "kg")
        self.assertEqual(result.amount, Decimal("500"))
        self.assertEqual(result.base_unit, "g")

    def test_convert_szczypta_to_g(self):
        result = convert_to_base(Decimal("2"), "szczypta")
        self.assertEqual(result.amount, Decimal("1"))  # 2 * 0.5g
        self.assertEqual(result.base_unit, "g")

    def test_convert_szt(self):
        result = convert_to_base(Decimal("5"), "szt")
        self.assertEqual(result.amount, Decimal("5"))
        self.assertEqual(result.base_unit, "szt")

    def test_format_amount_ml_small(self):
        amount, unit = format_amount(Decimal("50"), "ml")
        self.assertEqual(amount, "50")
        self.assertEqual(unit, "ml")

    def test_format_amount_ml_to_liters(self):
        amount, unit = format_amount(Decimal("1500"), "ml")
        self.assertEqual(amount, "1.5")
        self.assertEqual(unit, "l")

    def test_format_amount_g_to_kg(self):
        amount, unit = format_amount(Decimal("2500"), "g")
        self.assertEqual(amount, "2.5")
        self.assertEqual(unit, "kg")

    def test_format_amount_g_small(self):
        amount, unit = format_amount(Decimal("200"), "g")
        self.assertEqual(amount, "200")
        self.assertEqual(unit, "g")


class AggregateIngredientsTest(TestCase):
    """Testy agregacji składników."""

    def test_aggregate_same_unit(self):
        """Sumowanie składników z tą samą jednostką."""
        data = [
            {
                "ingredient_id": 1,
                "ingredient_name": "Mąka",
                "ingredient_category": "sypkie",
                "amount": Decimal("200"),
                "unit": "g",
            },
            {
                "ingredient_id": 1,
                "ingredient_name": "Mąka",
                "ingredient_category": "sypkie",
                "amount": Decimal("300"),
                "unit": "g",
            },
        ]
        result = aggregate_ingredients(data)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["ingredient_name"], "Mąka")
        self.assertEqual(result[0]["base_amount"], Decimal("500"))
        self.assertEqual(result[0]["display_amount"], "500")
        self.assertEqual(result[0]["display_unit"], "g")

    def test_aggregate_different_units_volume(self):
        """Sumowanie mleka: łyżeczka + ml → ml."""
        data = [
            {
                "ingredient_id": 1,
                "ingredient_name": "Mleko",
                "ingredient_category": "nabiał",
                "amount": Decimal("2"),
                "unit": "łyżeczka",
            },
            {
                "ingredient_id": 1,
                "ingredient_name": "Mleko",
                "ingredient_category": "nabiał",
                "amount": Decimal("100"),
                "unit": "ml",
            },
        ]
        result = aggregate_ingredients(data)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["ingredient_name"], "Mleko")
        # 2 * 5ml + 100ml = 110ml
        self.assertEqual(result[0]["base_amount"], Decimal("110"))
        self.assertEqual(result[0]["display_amount"], "110")
        self.assertEqual(result[0]["display_unit"], "ml")

    def test_aggregate_different_units_weight(self):
        """Sumowanie mąki: g + kg → g/kg."""
        data = [
            {
                "ingredient_id": 1,
                "ingredient_name": "Mąka",
                "ingredient_category": "sypkie",
                "amount": Decimal("500"),
                "unit": "g",
            },
            {
                "ingredient_id": 1,
                "ingredient_name": "Mąka",
                "ingredient_category": "sypkie",
                "amount": Decimal("1"),
                "unit": "kg",
            },
        ]
        result = aggregate_ingredients(data)

        self.assertEqual(len(result), 1)
        # 500g + 1000g = 1500g = 1.5kg
        self.assertEqual(result[0]["base_amount"], Decimal("1500"))
        self.assertEqual(result[0]["display_amount"], "1.5")
        self.assertEqual(result[0]["display_unit"], "kg")

    def test_aggregate_multiple_ingredients(self):
        """Różne składniki są oddzielnie."""
        data = [
            {
                "ingredient_id": 1,
                "ingredient_name": "Mleko",
                "ingredient_category": "nabiał",
                "amount": Decimal("200"),
                "unit": "ml",
            },
            {
                "ingredient_id": 2,
                "ingredient_name": "Mąka",
                "ingredient_category": "sypkie",
                "amount": Decimal("300"),
                "unit": "g",
            },
        ]
        result = aggregate_ingredients(data)

        self.assertEqual(len(result), 2)
        names = {r["ingredient_name"] for r in result}
        self.assertEqual(names, {"Mleko", "Mąka"})

    def test_aggregate_preserves_original_entries(self):
        """Zachowuje oryginalne wpisy do wyświetlenia."""
        data = [
            {
                "ingredient_id": 1,
                "ingredient_name": "Mleko",
                "ingredient_category": "nabiał",
                "amount": Decimal("2"),
                "unit": "łyżeczka",
            },
            {
                "ingredient_id": 1,
                "ingredient_name": "Mleko",
                "ingredient_category": "nabiał",
                "amount": Decimal("100"),
                "unit": "ml",
            },
        ]
        result = aggregate_ingredients(data)

        self.assertEqual(len(result[0]["original_entries"]), 2)


class ShoppingViewTest(TestCase):
    """Testy widoku listy zakupów."""

    def setUp(self):
        # Utwórz składniki
        self.milk = Ingredient.objects.create(name="Mleko", category="nabiał")
        self.flour = Ingredient.objects.create(name="Mąka", category="sypkie")

        # Utwórz przepisy
        self.recipe1 = Recipe.objects.create(name="Naleśniki", preparation_time=30)
        self.recipe2 = Recipe.objects.create(name="Ciasto", preparation_time=60)

        # Dodaj składniki do przepisów
        RecipeIngredient.objects.create(recipe=self.recipe1, ingredient=self.milk, amount=Decimal("2"), unit="łyżeczka")
        RecipeIngredient.objects.create(recipe=self.recipe1, ingredient=self.flour, amount=Decimal("200"), unit="g")
        RecipeIngredient.objects.create(recipe=self.recipe2, ingredient=self.milk, amount=Decimal("100"), unit="ml")
        RecipeIngredient.objects.create(recipe=self.recipe2, ingredient=self.flour, amount=Decimal("300"), unit="g")

        # Utwórz plan
        self.plan = MealPlan.objects.create(
            name="Tydzień 1",
            day_of_week="Poniedziałek",
            recipe_dinner=self.recipe1,
            recipe_supper=self.recipe2,
        )

    def test_shopping_index_without_plan(self):
        response = self.client.get(reverse("shopping:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Wybierz plan posiłków")

    def test_shopping_index_with_plan(self):
        response = self.client.get(reverse("shopping:index"), {"plan": "Tydzień 1"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Mleko")
        self.assertContains(response, "Mąka")

    def test_shopping_aggregates_units(self):
        """Sprawdza, że składniki są sumowane z konwersją jednostek."""
        response = self.client.get(reverse("shopping:index"), {"plan": "Tydzień 1"})

        # Mleko: 2 łyżeczki (10ml) + 100ml = 110ml
        self.assertContains(response, "110")
        self.assertContains(response, "ml")

        # Mąka: 200g + 300g = 500g
        self.assertContains(response, "500")
        self.assertContains(response, "g")

    def test_shopping_grouping_case_insensitive(self):
        """Kategoria powinna być grupowana case-insensitive (nie duplikować grup)."""
        # Utwórz składniki z tą samą kategorią różniącą się tylko wielkością liter
        ing1 = Ingredient.objects.create(name="Ser", category="nabiał")
        ing2 = Ingredient.objects.create(name="Jogurt", category="NABIAŁ")

        # Utwórz przepisy i przypisz składniki
        r1 = Recipe.objects.create(name="R1", preparation_time=10)
        r2 = Recipe.objects.create(name="R2", preparation_time=10)
        RecipeIngredient.objects.create(recipe=r1, ingredient=ing1, amount=1, unit="szt")
        RecipeIngredient.objects.create(recipe=r2, ingredient=ing2, amount=1, unit="szt")

        # Plan zawierający oba przepisy
        MealPlan.objects.create(
            name="PlanCase",
            day_of_week="Wtorek",
            recipe_dinner=r1,
            recipe_supper=r2,
        )

        response = self.client.get(reverse("shopping:index"), {"plan": "PlanCase"})
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        # Powinien pojawić się dokładnie jeden badge kategorii
        badge_count = content.count('<span class="badge bg-light text-dark">')
        self.assertEqual(badge_count, 1)
