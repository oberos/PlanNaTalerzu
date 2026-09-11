from django.db import models


DAY_CHOICES = [
    ("Poniedziałek", "Poniedziałek"),
    ("Wtorek", "Wtorek"),
    ("Środa", "Środa"),
    ("Czwartek", "Czwartek"),
    ("Piątek", "Piątek"),
    ("Sobota", "Sobota"),
    ("Niedziela", "Niedziela"),
]


class MealPlan(models.Model):
    name = models.CharField(max_length=200)
    day_of_week = models.CharField(max_length=15, choices=DAY_CHOICES)
    recipe_dinner = models.ForeignKey(
        "recipes.Recipe",
        on_delete=models.CASCADE,
        related_name="mealplan_dinner",
        blank=True,
        null=True,
    )
    recipe_dinner_alternative = models.ForeignKey(
        "recipes.Recipe",
        on_delete=models.CASCADE,
        related_name="mealplan_dinner_alternative",
        blank=True,
        null=True,
    )
    recipe_supper = models.ForeignKey(
        "recipes.Recipe",
        on_delete=models.CASCADE,
        related_name="mealplan_supper",
        blank=True,
        null=True,
    )
    recipe_breakfast = models.ForeignKey(
        "recipes.Recipe",
        on_delete=models.CASCADE,
        related_name="mealplan_breakfast",
        blank=True,
        null=True,
    )
    recipe_second_breakfast = models.ForeignKey(
        "recipes.Recipe",
        on_delete=models.CASCADE,
        related_name="mealplan_second_breakfast",
        blank=True,
        null=True,
    )

    class Meta:
        ordering = ["name", "day_of_week"]

    def __str__(self) -> str:
        return f"{self.name} - {self.day_of_week}"


class MealItem(models.Model):
    MEAL_CHOICES = [
        ("breakfast", "Śniadanie"),
        ("second_breakfast", "II Śniadanie"),
        ("dinner", "Obiad"),
        ("supper", "Kolacja"),
        ("alternative", "Obiad"),
    ]
    TYPE_CHOICES = [
        ("recipe", "Przepis"),
        ("ingredient", "Składnik"),
    ]

    mealplan = models.ForeignKey(MealPlan, on_delete=models.CASCADE, related_name="items")
    meal = models.CharField(max_length=32, choices=MEAL_CHOICES)
    type = models.CharField(max_length=16, choices=TYPE_CHOICES)
    recipe = models.ForeignKey(
        "recipes.Recipe", on_delete=models.CASCADE, blank=True, null=True, related_name="meal_items"
    )
    ingredient_name = models.CharField(max_length=200, blank=True)
    ingredient_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    ingredient_unit = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    # persisted nutrition snapshot (per item)
    calories = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    protein = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    carbohydrates = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    fat = models.DecimalField(max_digits=8, decimal_places=2, default=0)

    class Meta:
        ordering = ["mealplan", "meal", "-created_at"]

    def __str__(self) -> str:
        if self.type == "recipe" and self.recipe:
            return f"{self.mealplan.name}:{self.meal} -> {self.recipe.name}"
        return f"{self.mealplan.name}:{self.meal} -> {self.ingredient_name}"
