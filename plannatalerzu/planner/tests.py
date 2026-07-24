from django.test import TestCase
from django.urls import reverse

from planner.models import MealPlan
from recipes.models import Recipe


class PlannerViewsTests(TestCase):
    def setUp(self):
        self.recipe_1 = Recipe.objects.create(name="Kotlet", description="Opis", preparation_time=20, servings=2)
        self.recipe_2 = Recipe.objects.create(name="Zupa", description="Opis", preparation_time=15, servings=4)
        self.meal_plan = MealPlan.objects.create(
            name="Plan tygodnia",
            day_of_week="Poniedziałek",
            recipe_dinner=None,
            recipe_dinner_alternative=None,
            recipe_supper=None,
        )

    def test_edit_mode_renders_recipe_selects_and_updates_plan(self):
        response = self.client.get(reverse("planner:index"), {"edit_plan": "Plan tygodnia"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'name="recipe_dinner_{}'.format(self.meal_plan.pk))

        response = self.client.post(
            reverse("planner:index"),
            {
                "action": "update",
                "planner_name": "Plan tygodnia",
                "recipe_dinner_{}".format(self.meal_plan.pk): str(self.recipe_1.pk),
                "recipe_supper_{}".format(self.meal_plan.pk): str(self.recipe_2.pk),
            },
        )

        self.meal_plan.refresh_from_db()
        self.assertEqual(self.meal_plan.recipe_dinner, self.recipe_1)
        self.assertEqual(self.meal_plan.recipe_supper, self.recipe_2)
        self.assertRedirects(response, reverse("planner:index"))
