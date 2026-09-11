"""Add nutrition fields to MealItem

Revision ID: 0005_add_mealitem_nutrition
Revises: 0004_add_recipe_breakfast
Create Date: 2026-09-11 16:20
"""

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("planner", "0004_add_recipe_breakfast"),
    ]

    operations = [
        migrations.AddField(
            model_name="mealitem",
            name="calories",
            field=models.DecimalField(default=0, max_digits=8, decimal_places=2),
        ),
        migrations.AddField(
            model_name="mealitem",
            name="protein",
            field=models.DecimalField(default=0, max_digits=8, decimal_places=2),
        ),
        migrations.AddField(
            model_name="mealitem",
            name="carbohydrates",
            field=models.DecimalField(default=0, max_digits=8, decimal_places=2),
        ),
        migrations.AddField(
            model_name="mealitem",
            name="fat",
            field=models.DecimalField(default=0, max_digits=8, decimal_places=2),
        ),
    ]
