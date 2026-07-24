from django.db import models


class Recipe(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
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
