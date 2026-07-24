# Modele danych

## Diagram relacji (ERD)

```
┌─────────────────────────┐       ┌─────────────────────────┐
│        Recipe           │       │       Ingredient        │
├─────────────────────────┤       ├─────────────────────────┤
│ id (PK)                 │       │ id (PK)                 │
│ name: VARCHAR(200)      │       │ name: VARCHAR(200)      │
│ description: TEXT       │       │ category: VARCHAR(100)  │
│ preparation_time: INT   │       │ default_unit: VARCHAR(50)│
│ servings: INT           │       └─────────────────────────┘
│ category: VARCHAR(100)  │                   │
│ image: ImageField       │                   │
└─────────────────────────┘                   │
            │                                 │
            │         ┌───────────────────────┴────────────┐
            │         │        RecipeIngredient            │
            │         ├────────────────────────────────────┤
            └────────►│ id (PK)                            │
                      │ recipe_id (FK) ───────────────────►│
                      │ ingredient_id (FK) ───────────────►│
                      │ amount: DECIMAL(8,2)               │
                      │ unit: VARCHAR(50)                  │
                      │ UNIQUE(recipe_id, ingredient_id)   │
                      └────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                        MealPlan                              │
├─────────────────────────────────────────────────────────────┤
│ id (PK)                                                      │
│ name: VARCHAR(200)                                           │
│ day_of_week: CHOICE (Poniedziałek..Niedziela)               │
│ recipe_dinner_id (FK) ─────────────────────────► Recipe      │
│ recipe_dinner_alternative_id (FK) ─────────────► Recipe      │
│ recipe_supper_id (FK) ─────────────────────────► Recipe      │
└─────────────────────────────────────────────────────────────┘
```

## Modele szczegółowo

### Recipe (Przepis)

Przechowuje informacje o przepisie kulinarnym.

```python
class Recipe(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    preparation_time = models.PositiveIntegerField(default=0)  # w minutach
    servings = models.PositiveIntegerField(default=1)
    category = models.CharField(max_length=100, blank=True)
    image = models.ImageField(upload_to="recipes/", blank=True, null=True)
```

**Atrybuty:**
| Pole | Typ | Opis | Wymagane |
|------|-----|------|----------|
| `name` | CharField(200) | Nazwa przepisu | Tak |
| `description` | TextField | Opis/instrukcja | Nie |
| `preparation_time` | PositiveIntegerField | Czas w minutach | Nie (default: 0) |
| `servings` | PositiveIntegerField | Liczba porcji | Nie (default: 1) |
| `category` | CharField(100) | Kategoria (np. "obiad") | Nie |
| `image` | ImageField | Zdjęcie przepisu | Nie |

**Relacje:**
- `ingredients` - związane składniki przez `RecipeIngredient`

**Meta:**
- Sortowanie: alfabetycznie po nazwie
- Verbose: "przepis" / "przepisy"

---

### Ingredient (Składnik)

Przechowuje informacje o składniku (produkt).

```python
class Ingredient(models.Model):
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=100, blank=True)
    default_unit = models.CharField(max_length=50, blank=True)
```

**Atrybuty:**
| Pole | Typ | Opis | Wymagane |
|------|-----|------|----------|
| `name` | CharField(200) | Nazwa składnika | Tak |
| `category` | CharField(100) | Kategoria (np. "warzywa") | Nie |
| `default_unit` | CharField(50) | Domyślna jednostka (g/ml/szt) | Nie |

**Relacje:**
- `recipes` - przepisy zawierające ten składnik

**Meta:**
- Sortowanie: alfabetycznie po nazwie
- Verbose: "składnik" / "składniki"

---

### RecipeIngredient (Składnik przepisu)

Model pośredni łączący przepis ze składnikiem z ilością.

```python
class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, related_name="ingredients", on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, related_name="recipes", on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    unit = models.CharField(max_length=50, blank=True)
```

**Atrybuty:**
| Pole | Typ | Opis | Wymagane |
|------|-----|------|----------|
| `recipe` | ForeignKey | Powiązany przepis | Tak |
| `ingredient` | ForeignKey | Powiązany składnik | Tak |
| `amount` | Decimal(8,2) | Ilość składnika | Nie (default: 0) |
| `unit` | CharField(50) | Jednostka (g/ml/szt) | Nie |

**Ograniczenia:**
- `unique_together = ("recipe", "ingredient")` - jeden składnik raz w przepisie

**Meta:**
- Sortowanie: po nazwie składnika
- Verbose: "składnik przepisu" / "składniki przepisów"

---

### MealPlan (Plan posiłków)

Przechowuje plan posiłków na konkretny dzień tygodnia.

```python
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
    recipe_dinner = models.ForeignKey(Recipe, null=True, blank=True, related_name="mealplan_dinner")
    recipe_dinner_alternative = models.ForeignKey(Recipe, null=True, blank=True, related_name="mealplan_dinner_alternative")
    recipe_supper = models.ForeignKey(Recipe, null=True, blank=True, related_name="mealplan_supper")
```

**Atrybuty:**
| Pole | Typ | Opis | Wymagane |
|------|-----|------|----------|
| `name` | CharField(200) | Nazwa planu (np. "Tydzień 1") | Tak |
| `day_of_week` | CharField(15) | Dzień tygodnia | Tak |
| `recipe_dinner` | ForeignKey | Przepis na obiad | Nie |
| `recipe_dinner_alternative` | ForeignKey | Alternatywny obiad | Nie |
| `recipe_supper` | ForeignKey | Przepis na kolację | Nie |

**Uwagi:**
- Jeden `MealPlan` = jeden dzień w tygodniu
- Plan tygodniowy = 7 rekordów `MealPlan` z tą samą nazwą
- Tworzenie planu automatycznie tworzy 7 dni

**Meta:**
- Sortowanie: po nazwie, potem dniu tygodnia

---

## Przykłady zapytań

### Pobranie wszystkich przepisów z ich składnikami

```python
recipes = Recipe.objects.prefetch_related("ingredients__ingredient").all()

for recipe in recipes:
    print(f"{recipe.name}:")
    for rel in recipe.ingredients.all():
        print(f"  - {rel.amount} {rel.unit} {rel.ingredient.name}")
```

### Pobranie planu tygodnia z przepisami

```python
from itertools import groupby

entries = MealPlan.objects.order_by("name")
for name, group in groupby(entries, key=lambda e: e.name):
    print(f"Plan: {name}")
    for day in group:
        dinner = day.recipe_dinner.name if day.recipe_dinner else "brak"
        print(f"  {day.day_of_week}: {dinner}")
```

### Agregacja składników dla listy zakupów

```python
from django.db.models import Sum
from collections import defaultdict

plan_name = "Mój plan"
plans = MealPlan.objects.filter(name=plan_name)

# Zbierz wszystkie przepisy
recipe_ids = set()
for plan in plans:
    for field in ['recipe_dinner', 'recipe_dinner_alternative', 'recipe_supper']:
        recipe = getattr(plan, field)
        if recipe:
            recipe_ids.add(recipe.id)

# Agreguj składniki
ingredients = RecipeIngredient.objects.filter(
    recipe_id__in=recipe_ids
).values(
    'ingredient__name', 'ingredient__category', 'unit'
).annotate(
    total=Sum('amount')
).order_by('ingredient__category', 'ingredient__name')
```

---

## Planowane modele (opcjonalne)

### ShoppingItem (Pozycja listy zakupów)

```python
class ShoppingItem(models.Model):
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    unit = models.CharField(max_length=50)
    is_purchased = models.BooleanField(default=False)
    meal_plan = models.ForeignKey(MealPlan, on_delete=models.CASCADE)
```

### NutritionInfo (Wartości odżywcze)

```python
class NutritionInfo(models.Model):
    ingredient = models.OneToOneField(Ingredient, on_delete=models.CASCADE)
    calories = models.DecimalField(max_digits=7, decimal_places=2)  # na 100g
    protein = models.DecimalField(max_digits=6, decimal_places=2)
    fat = models.DecimalField(max_digits=6, decimal_places=2)
    carbohydrates = models.DecimalField(max_digits=6, decimal_places=2)
```
