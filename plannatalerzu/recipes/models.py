from decimal import Decimal

from django.db import models


class Recipe(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    instructions = models.TextField(blank=True, help_text="Kroki przygotowania (każdy krok w nowej linii)")
    preparation_time = models.PositiveIntegerField(default=0, help_text="Czas przygotowania w minutach")
    servings = models.PositiveIntegerField(default=1)
    category = models.CharField(max_length=100, blank=True)
    image = models.ImageField(upload_to="recipes/", blank=True, null=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "przepis"
        verbose_name_plural = "przepisy"

    def __str__(self):
        return self.name

    def calculate_nutrition(self):
        """
        Oblicza łączne wartości odżywcze dla przepisu na podstawie składników.
        Zwraca słownik z wartościami dla całego przepisu i na porcję.
        """
        # Mapowanie jednostek na gramy/mililitry
        unit_to_grams = {
            "g": Decimal("1"),
            "kg": Decimal("1000"),
            "dag": Decimal("10"),
            "mg": Decimal("0.001"),
            "ml": Decimal("1"),  # Zakładamy gęstość wody ~1g/ml
            "l": Decimal("1000"),
            "łyżka": Decimal("15"),
            "łyżeczka": Decimal("5"),
            "szklanka": Decimal("250"),
            "szczypta": Decimal("0.5"),
            "szt": Decimal("100"),  # Zakładamy średnio 100g na sztukę
        }

        totals = {
            "calories": Decimal("0"),
            "protein": Decimal("0"),
            "carbohydrates": Decimal("0"),
            "fat": Decimal("0"),
            "fiber": Decimal("0"),
            "has_nutrition_data": False,
            "ingredients_with_data": 0,
            "ingredients_without_data": 0,
        }

        for recipe_ingredient in self.ingredients.select_related("ingredient__nutrition").all():
            try:
                nutrition = recipe_ingredient.ingredient.nutrition
            except NutritionInfo.DoesNotExist:
                totals["ingredients_without_data"] += 1
                continue

            # Konwertuj ilość na gramy
            unit = recipe_ingredient.unit.lower().strip()
            conversion_factor = unit_to_grams.get(unit, Decimal("1"))
            amount_in_grams = recipe_ingredient.amount * conversion_factor

            # Oblicz wartości odżywcze (dane są na 100g)
            multiplier = amount_in_grams / Decimal("100")

            totals["calories"] += nutrition.calories * multiplier
            totals["protein"] += nutrition.protein * multiplier
            totals["carbohydrates"] += nutrition.carbohydrates * multiplier
            totals["fat"] += nutrition.fat * multiplier
            totals["fiber"] += nutrition.fiber * multiplier
            totals["has_nutrition_data"] = True
            totals["ingredients_with_data"] += 1

        # Zaokrąglij wartości
        for key in ["calories", "protein", "carbohydrates", "fat", "fiber"]:
            totals[key] = round(totals[key], 1)

        # Oblicz wartości na porcję
        servings = self.servings if self.servings > 0 else 1
        per_serving = {
            "calories": round(totals["calories"] / servings, 1),
            "protein": round(totals["protein"] / servings, 1),
            "carbohydrates": round(totals["carbohydrates"] / servings, 1),
            "fat": round(totals["fat"] / servings, 1),
            "fiber": round(totals["fiber"] / servings, 1),
        }

        return {
            "total": totals,
            "per_serving": per_serving,
            "servings": servings,
        }


class Ingredient(models.Model):
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=100, blank=True)
    default_unit = models.CharField(max_length=50, blank=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "składnik"
        verbose_name_plural = "składniki"

    def __str__(self):
        return self.name


class NutritionInfo(models.Model):
    """Wartości odżywcze na 100g/100ml składnika."""

    ingredient = models.OneToOneField(
        Ingredient,
        on_delete=models.CASCADE,
        related_name="nutrition",
        verbose_name="składnik",
    )
    calories = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        default=0,
        help_text="Kalorie (kcal) na 100g/100ml",
        verbose_name="kalorie (kcal)",
    )
    protein = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=0,
        help_text="Białko (g) na 100g/100ml",
        verbose_name="białko (g)",
    )
    carbohydrates = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=0,
        help_text="Węglowodany (g) na 100g/100ml",
        verbose_name="węglowodany (g)",
    )
    fat = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=0,
        help_text="Tłuszcze (g) na 100g/100ml",
        verbose_name="tłuszcze (g)",
    )
    fiber = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=0,
        help_text="Błonnik (g) na 100g/100ml",
        verbose_name="błonnik (g)",
    )

    class Meta:
        verbose_name = "wartości odżywcze"
        verbose_name_plural = "wartości odżywcze"

    def __str__(self):
        return f"Wartości odżywcze: {self.ingredient.name}"


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, related_name="ingredients", on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, related_name="recipes", on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    unit = models.CharField(max_length=50, blank=True)

    class Meta:
        ordering = ["ingredient__name"]
        unique_together = ("recipe", "ingredient")
        verbose_name = "składnik przepisu"
        verbose_name_plural = "składniki przepisów"

    def __str__(self):
        return f"{self.amount} {self.unit} {self.ingredient.name} w {self.recipe.name}"
