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

    class Meta:
        ordering = ["name", "day_of_week"]

    def __str__(self) -> str:
        return f"{self.name} - {self.day_of_week}"
