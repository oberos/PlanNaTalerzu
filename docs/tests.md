# Testy

## Przegląd pokrycia

| Aplikacja | Modele | Widoki | Status |
|-----------|--------|--------|--------|
| recipes | ✅ Tak | ✅ Tak | Dobre pokrycie |
| planner | ❌ Nie | ✅ Tak | Częściowe |
| shopping | ✅ Tak | ✅ Tak | **20 testów** (konwersja jednostek) |

---

## Istniejące testy

### shopping/tests.py

#### UnitConverterTest (12 testów)

Testy konwersji jednostek:
- `test_convert_ml_to_base` - ml bez konwersji
- `test_convert_liter_to_ml` - litry → ml
- `test_convert_lyżeczka_to_ml` - łyżeczka (5ml) → ml
- `test_convert_lyżka_to_ml` - łyżka (15ml) → ml
- `test_convert_szklanka_to_ml` - szklanka (250ml) → ml
- `test_convert_kg_to_g` - kg → g
- `test_convert_szczypta_to_g` - szczypta (0.5g) → g
- `test_convert_szt` - sztuki bez konwersji
- `test_format_amount_ml_small` - formatowanie <1000ml
- `test_format_amount_ml_to_liters` - formatowanie ≥1000ml → l
- `test_format_amount_g_to_kg` - formatowanie ≥1000g → kg
- `test_format_amount_g_small` - formatowanie <1000g

#### AggregateIngredientsTest (5 testów)

Testy agregacji składników:
- `test_aggregate_same_unit` - sumowanie z tą samą jednostką
- `test_aggregate_different_units_volume` - łyżeczka + ml
- `test_aggregate_different_units_weight` - g + kg
- `test_aggregate_multiple_ingredients` - różne składniki
- `test_aggregate_preserves_original_entries` - zachowanie oryginalnych wpisów

#### ShoppingViewTest (3 testy)

- `test_shopping_index_without_plan` - widok bez wybranego planu
- `test_shopping_index_with_plan` - widok z planem
- `test_shopping_aggregates_units` - integracyjny test konwersji

---

### recipes/tests.py

#### RecipeModelsTest

```python
test_recipe_with_ingredients_can_be_created()
```
- Tworzy przepis z jednym składnikiem
- Sprawdza relację Recipe → RecipeIngredient → Ingredient
- Weryfikuje poprawność pól

#### RecipeViewsTest

```python
test_create_recipe_with_existing_and_new_ingredients()
```
- POST do tworzenia przepisu
- Dodaje istniejący i nowy składnik
- Sprawdza redirect, utworzenie Recipe i Ingredient
- Weryfikuje RecipeIngredient relations

```python
test_edit_recipe_adds_new_ingredients()
```
- Tworzy przepis z jednym składnikiem
- POST update z `new_ingredients` field
- Sprawdza dodanie nowego składnika
- Weryfikuje count RecipeIngredient

---

### planner/tests.py

#### PlannerViewsTests

```python
setUp()
```
- Tworzy 2 przepisy (Kotlet, Zupa)
- Tworzy MealPlan na Poniedziałek

```python
test_edit_mode_renders_recipe_selects_and_updates_plan()
```
- GET z `edit_plan` query param
- Sprawdza renderowanie selectów
- POST update z przypisaniem przepisów
- Weryfikuje zapisanie w bazie

---

## Brakujące testy

### recipes

- [ ] `test_delete_recipe`
- [ ] `test_create_recipe_validation_errors`
- [ ] `test_update_recipe_changes_fields`
- [ ] `test_index_displays_recipes`
- [ ] `test_edit_mode_shows_form`

### planner

- [ ] `test_create_plan_creates_7_days`
- [ ] `test_delete_plan_removes_all_days`
- [ ] `test_index_groups_by_plan_name`
- [ ] `test_day_order_is_correct`
- [ ] Model tests

### shopping

- [ ] `test_index_renders`
- [ ] `test_shopping_list_aggregation` (po implementacji)
- [ ] `test_filter_by_plan`

---

## Uruchamianie testów

```bash
# Wszystkie testy
cd plannatalerzu
pdm run python manage.py test

# Konkretna aplikacja
pdm run python manage.py test recipes
pdm run python manage.py test planner

# Konkretna klasa
pdm run python manage.py test recipes.tests.RecipeViewsTest

# Konkretny test
pdm run python manage.py test recipes.tests.RecipeViewsTest.test_create_recipe_with_existing_and_new_ingredients

# Verbose output
pdm run python manage.py test -v 2

# Coverage (wymaga pytest-cov)
pdm run pytest --cov=. --cov-report=html
```

---

## Wzorce testów

### Test modelu

```python
class RecipeModelTest(TestCase):
    def test_str_returns_name(self):
        recipe = Recipe.objects.create(name="Spaghetti")
        self.assertEqual(str(recipe), "Spaghetti")
    
    def test_default_values(self):
        recipe = Recipe.objects.create(name="Test")
        self.assertEqual(recipe.preparation_time, 0)
        self.assertEqual(recipe.servings, 1)
```

### Test widoku GET

```python
class RecipeViewTest(TestCase):
    def test_index_returns_200(self):
        response = self.client.get(reverse("recipes:index"))
        self.assertEqual(response.status_code, 200)
    
    def test_index_uses_correct_template(self):
        response = self.client.get(reverse("recipes:index"))
        self.assertTemplateUsed(response, "recipes/index.html")
    
    def test_index_context_contains_recipes(self):
        Recipe.objects.create(name="Test")
        response = self.client.get(reverse("recipes:index"))
        self.assertIn("recipes", response.context)
        self.assertEqual(len(response.context["recipes"]), 1)
```

### Test widoku POST

```python
class RecipeCreateTest(TestCase):
    def test_create_valid_recipe(self):
        response = self.client.post(reverse("recipes:index"), {
            "action": "create",
            "name": "New Recipe",
            "description": "Description",
            "preparation_time": 30,
            "servings": 4,
            "category": "dinner",
        })
        self.assertRedirects(response, reverse("recipes:index"))
        self.assertTrue(Recipe.objects.filter(name="New Recipe").exists())
    
    def test_create_empty_name_fails(self):
        count_before = Recipe.objects.count()
        response = self.client.post(reverse("recipes:index"), {
            "action": "create",
            "name": "",
        })
        # Depends on validation implementation
        self.assertEqual(Recipe.objects.count(), count_before)
```

### Test z fixture

```python
class MealPlanTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        """Dane współdzielone przez wszystkie testy w klasie"""
        cls.recipe = Recipe.objects.create(
            name="Shared Recipe",
            preparation_time=20,
        )
    
    def setUp(self):
        """Dane dla każdego testu osobno"""
        self.plan = MealPlan.objects.create(
            name="Test Plan",
            day_of_week="Poniedziałek",
        )
```

---

## Konfiguracja testów

### pytest.ini (opcjonalne)

```ini
[pytest]
DJANGO_SETTINGS_MODULE = plannatalerzu.settings
python_files = tests.py test_*.py
addopts = -v --tb=short
```

### Osobne ustawienia testowe

```python
# plannatalerzu/settings_test.py
from .settings import *

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
```

```bash
pdm run python manage.py test --settings=plannatalerzu.settings_test
```
