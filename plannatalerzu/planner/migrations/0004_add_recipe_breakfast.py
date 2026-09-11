"""Add recipe_breakfast and recipe_second_breakfast to MealPlan

Revision ID: 0004_add_recipe_breakfast
Revises: 0003_add_mealitem
Create Date: 2026-09-11 15:40
"""

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("planner", "0003_add_mealitem"),
        ("recipes", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="mealplan",
            name="recipe_breakfast",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="mealplan_breakfast",
                to="recipes.recipe",
            ),
        ),
        migrations.AddField(
            model_name="mealplan",
            name="recipe_second_breakfast",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="mealplan_second_breakfast",
                to="recipes.recipe",
            ),
        ),
    ]
