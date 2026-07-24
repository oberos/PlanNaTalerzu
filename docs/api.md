# API i widoki

## Routing URL

### Główne ścieżki

| URL | Nazwa | Widok | Metody |
|-----|-------|-------|--------|
| `/` | `home` | `plannatalerzu.views.home` | GET |
| `/admin/` | - | Django Admin | GET, POST |
| `/recipes/` | `recipes:index` | `recipes.views.recipe_index` | GET, POST |
| `/planner/` | `planner:index` | `planner.views.planner_index` | GET, POST |
| `/shopping/` | `shopping:index` | `shopping.views.shopping_index` | GET |

---

## Widoki szczegółowo

### home (Strona główna)

**URL:** `/`  
**Metoda:** GET  
**Szablon:** `home.html`

**Kontekst:**
```python
{"page_title": "PlanNaTalerzu"}
```

**Opis:**
Landing page z linkami do planowania i przepisów.

---

### recipe_index (Przepisy)

**URL:** `/recipes/`  
**Metody:** GET, POST  
**Szablon:** `recipes/index.html`

#### GET - Lista przepisów

**Query params:**
| Param | Typ | Opis |
|-------|-----|------|
| `edit` | int | ID przepisu do edycji |

**Kontekst:**
```python
{
    "page_title": "Przepisy",
    "recipes": QuerySet[Recipe],        # wszystkie przepisy z prefetch
    "ingredients": QuerySet[Ingredient], # wszystkie składniki (select)
    "editing_recipe": Recipe | None,     # przepis do edycji
}
```

#### POST - Operacje CRUD

**Akcja: create** - Tworzenie przepisu

| Pole | Typ | Wymagane | Opis |
|------|-----|----------|------|
| `action` | string | Tak | "create" |
| `name` | string | Tak | Nazwa przepisu |
| `description` | string | Nie | Opis |
| `preparation_time` | int | Nie | Czas w min |
| `servings` | int | Nie | Porcje |
| `category` | string | Nie | Kategoria |
| `ingredient_id[]` | int[] | Nie | ID istniejących składników |
| `ingredient_amount[]` | decimal[] | Nie | Ilości |
| `ingredient_unit[]` | string[] | Nie | Jednostki |
| `new_ingredient_name[]` | string[] | Nie | Nazwy nowych składników |
| `new_ingredient_amount[]` | decimal[] | Nie | Ilości nowych |
| `new_ingredient_unit[]` | string[] | Nie | Jednostki nowych |
| `new_ingredients` | string | Nie | Lista składników (przecinki) |

**Odpowiedź:** Redirect do `/recipes/`

---

**Akcja: update** - Aktualizacja przepisu

| Pole | Typ | Wymagane | Opis |
|------|-----|----------|------|
| `action` | string | Tak | "update" |
| `recipe_id` | int | Tak | ID przepisu |
| (pozostałe jak create) |

**Odpowiedź:** Redirect do `/recipes/`

---

**Akcja: delete** - Usuwanie przepisu

| Pole | Typ | Wymagane | Opis |
|------|-----|----------|------|
| `action` | string | Tak | "delete" |
| `recipe_id` | int | Tak | ID przepisu |

**Odpowiedź:** Redirect do `/recipes/`

---

### planner_index (Planowanie)

**URL:** `/planner/`  
**Metody:** GET, POST  
**Szablon:** `planner/index.html`

#### GET - Lista planów

**Query params:**
| Param | Typ | Opis |
|-------|-----|------|
| `edit_plan` | string | Nazwa planu do edycji |

**Kontekst:**
```python
{
    "page_title": "Planowanie",
    "planners": [
        {
            "name": str,              # nazwa planu
            "rows": [MealPlan, ...],  # 7 dni posortowanych
            "edit_mode": bool,        # czy w trybie edycji
        },
        ...
    ],
    "recipes": QuerySet[Recipe],      # wszystkie przepisy (select)
}
```

#### POST - Operacje CRUD

**Akcja: create** - Tworzenie planu

| Pole | Typ | Wymagane | Opis |
|------|-----|----------|------|
| `action` | string | Tak | "create" |
| `name` | string | Tak | Nazwa planu |

**Logika:** Tworzy 7 rekordów `MealPlan` (jeden na każdy dzień).

**Odpowiedź:** Redirect do `/planner/`

---

**Akcja: update** - Aktualizacja planu

| Pole | Typ | Wymagane | Opis |
|------|-----|----------|------|
| `action` | string | Tak | "update" |
| `planner_name` | string | Tak | Nazwa planu |
| `recipe_dinner_{id}` | int | Nie | ID przepisu na obiad |
| `recipe_supper_{id}` | int | Nie | ID przepisu na kolację |
| `recipe_dinner_alternative_{id}` | int | Nie | ID alternatywy |

**Odpowiedź:** Redirect do `/planner/`

---

**Akcja: delete** - Usuwanie planu

| Pole | Typ | Wymagane | Opis |
|------|-----|----------|------|
| `action` | string | Tak | "delete" |
| `plan_name` | string | Tak | Nazwa planu |

**Logika:** Usuwa wszystkie rekordy MealPlan o danej nazwie.

**Odpowiedź:** Redirect do `/planner/`

---

### shopping_index (Lista zakupów)

**URL:** `/shopping/`  
**Metody:** GET  
**Szablon:** `shopping/index.html`

#### GET - Lista zakupów z konwersją jednostek

**Query params:**
| Param | Typ | Opis |
|-------|-----|------|
| `plan` | string | Nazwa planu do wygenerowania listy |

**Kontekst:**
```python
{
    "page_title": "Lista zakupów",
    "available_plans": QuerySet,     # dostępne plany
    "selected_plan": str,            # wybrany plan
    "shopping_list": list,           # zagregowana lista składników
    "grouped_list": list,            # lista pogrupowana po kategoriach
}
```

**Logika konwersji jednostek:**
1. Pobiera wszystkie przepisy z wybranego planu
2. Konwertuje jednostki do bazowych (ml, g, szt)
3. Sumuje identyczne składniki
4. Formatuje do czytelnych jednostek (>1000ml → l)

**Moduł:** `shopping/unit_converter.py`

---

## Funkcje pomocnicze (recipes/views.py)

### _parse_new_ingredients(raw_value)

Parsuje string ze składnikami oddzielonymi przecinkami lub nowymi liniami.

```python
_parse_new_ingredients("marchewka, cebula\npomidor")
# ["marchewka", "cebula", "pomidor"]
```

### _parse_amount(raw_value)

Konwertuje string na Decimal, obsługuje przecinek jako separator.

```python
_parse_amount("2,5")  # Decimal("2.5")
_parse_amount("")     # Decimal("0")
```

### _add_recipe_ingredient(recipe, ...)

Dodaje składnik do przepisu. Tworzy nowy Ingredient jeśli nie istnieje.

**Parametry:**
- `recipe` - przepis
- `ingredient` / `ingredient_id` / `ingredient_name` - składnik
- `amount`, `unit` - ilość i jednostka

---

## Panel administracyjny

### RecipeAdmin

- **list_display:** name, category, preparation_time, servings
- **search_fields:** name, category

### IngredientAdmin

- **list_display:** name, category, default_unit
- **search_fields:** name, category

### RecipeIngredientAdmin

- **list_display:** recipe, ingredient, amount, unit
- **search_fields:** recipe__name, ingredient__name

### MealPlanAdmin

- **list_display:** name, day_of_week, recipe_dinner, recipe_supper
- **list_filter:** name, day_of_week
- **search_fields:** name, recipe_dinner__name, recipe_dinner_alternative__name, recipe_supper__name

---

## Szablony

### base.html

Szablon bazowy z Bootstrap 5. Definiuje bloki:
- `{% block title %}` - tytuł strony
- `{% block content %}` - treść główna

### recipes/index.html

Dwukolumnowy layout:
- Lewa kolumna: formularz dodawania/edycji przepisu
- Prawa kolumna: lista przepisów z przyciskami akcji

JavaScript: dynamiczne dodawanie wierszy składników.

### planner/index.html

- Formularz tworzenia nowego planu
- Lista planów jako karty z tabelami (dzień | obiad | kolacja | alternatywa)
- Modal z szczegółami przepisu (Bootstrap modal)

### shopping/index.html

Placeholder z komunikatem i linkiem powrotu.
