"""Add MealItem model

Revision ID: 0003_add_mealitem
Revises: 0002_alter_mealplan_options_remove_mealplan_created_at_and_more
Create Date: 2026-09-11 14:15
"""

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("planner", "0002_alter_mealplan_options_remove_mealplan_created_at_and_more"),
        ("recipes", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="MealItem",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "meal",
                    models.CharField(
                        choices=[("dinner", "Obiad"), ("supper", "Kolacja"), ("alternative", "Alternatywa")],
                        max_length=32,
                    ),
                ),
                ("type", models.CharField(choices=[("recipe", "Przepis"), ("ingredient", "Składnik")], max_length=16)),
                ("ingredient_name", models.CharField(blank=True, max_length=200)),
                ("ingredient_amount", models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ("ingredient_unit", models.CharField(blank=True, max_length=50)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "recipe",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="meal_items",
                        to="recipes.recipe",
                    ),
                ),
                (
                    "mealplan",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, related_name="items", to="planner.mealplan"
                    ),
                ),
            ],
            options={
                "ordering": ["mealplan", "meal", "-created_at"],
            },
        ),
    ]
