# Przewodnik deweloperski

## Wymagania

- Python 3.14.x
- PDM (Python Dependency Manager)
- Git

## Szybki start

### 1. Klonowanie i setup

```bash
git clone <repo-url>
cd PlanNaTalerzu
```

### 2. Instalacja zależności (PDM)

```bash
pdm install
```

### 3. Aktywacja środowiska

```bash
# Windows PowerShell
.venv\Scripts\Activate.ps1

# Windows CMD
.venv\Scripts\activate.bat

# Linux/macOS
source .venv/bin/activate
```

### 4. Migracje bazy danych

```bash
cd plannatalerzu
pdm run python manage.py migrate
```

### 5. Tworzenie superużytkownika (opcjonalne)

```bash
pdm run python manage.py createsuperuser
```

### 6. Uruchomienie serwera

```bash
pdm run python manage.py runserver 8081
```

Aplikacja dostępna pod: http://127.0.0.1:8081/

---

## Struktura katalogów

```
PlanNaTalerzu/
├── pyproject.toml           # Zależności PDM
├── .venv/                   # Środowisko wirtualne
├── docs/                    # Dokumentacja
├── plannatalerzu/           # Projekt Django
│   ├── manage.py
│   ├── db.sqlite3
│   ├── plannatalerzu/       # Moduł główny (settings, urls)
│   ├── recipes/             # App: przepisy
│   ├── planner/             # App: planowanie
│   ├── shopping/            # App: lista zakupów
│   └── templates/           # Szablony globalne
```

---

## Polecenia Django

### Migracje

```bash
# Tworzenie nowych migracji
pdm run python manage.py makemigrations

# Aplikowanie migracji
pdm run python manage.py migrate

# Status migracji
pdm run python manage.py showmigrations
```

### Testy

```bash
# Wszystkie testy
pdm run python manage.py test

# Testy konkretnej aplikacji
pdm run python manage.py test recipes
pdm run python manage.py test planner

# Z verbose
pdm run python manage.py test -v 2
```

### Shell Django

```bash
pdm run python manage.py shell
```

```python
# Przykładowe zapytania
from recipes.models import Recipe, Ingredient

Recipe.objects.all()
Recipe.objects.create(name="Test", description="Opis")
```

### Kolekcja statycznych plików

```bash
pdm run python manage.py collectstatic
```

---

## Dodawanie nowej funkcjonalności

### 1. Nowa aplikacja Django

```bash
cd plannatalerzu
pdm run python manage.py startapp nazwa_aplikacji
```

Następnie dodaj do `INSTALLED_APPS` w `settings.py`.

### 2. Nowy model

1. Zdefiniuj model w `models.py`
2. Utwórz migrację: `makemigrations`
3. Zastosuj migrację: `migrate`
4. Zarejestruj w admin: `admin.py`

### 3. Nowy widok

1. Funkcja w `views.py`
2. Ścieżka URL w `urls.py`
3. Szablon w `templates/<app>/<nazwa>.html`

---

## Konwencje kodu

### Python

- PEP 8 (formatowanie)
- Docstrings dla funkcji publicznych
- Type hints (rekomendowane)
- Import sortowanie: stdlib, third-party, local

### Django

- Nazwy modeli: CamelCase, liczba pojedyncza (`Recipe`, nie `Recipes`)
- Nazwy pól: snake_case
- Related names: opisowe (`ingredients`, nie `recipeingredient_set`)
- Widoki: funkcje dla prostych, klasy dla złożonych

### Szablony

- Dziedziczenie z `base.html`
- Nazwy plików: snake_case
- Używaj bloków `{% block %}` zamiast duplikacji

### JavaScript

- Vanilla JS (bez frameworków)
- `DOMContentLoaded` dla event listeners
- Defensywne sprawdzanie elementów

---

## Testowanie

### Struktura testów

```python
# recipes/tests.py
from django.test import TestCase
from django.urls import reverse
from .models import Recipe

class RecipeModelsTest(TestCase):
    def test_recipe_creation(self):
        recipe = Recipe.objects.create(name="Test")
        self.assertEqual(recipe.name, "Test")

class RecipeViewsTest(TestCase):
    def test_index_get(self):
        response = self.client.get(reverse("recipes:index"))
        self.assertEqual(response.status_code, 200)
```

### Fixtures

```python
def setUp(self):
    self.recipe = Recipe.objects.create(
        name="Test Recipe",
        description="Test",
        preparation_time=30,
        servings=4,
    )
```

---

## Debugowanie

### Django Debug Toolbar

```bash
pdm add django-debug-toolbar
```

```python
# settings.py
INSTALLED_APPS += ["debug_toolbar"]
MIDDLEWARE += ["debug_toolbar.middleware.DebugToolbarMiddleware"]
INTERNAL_IPS = ["127.0.0.1"]
```

### Logowanie

```python
import logging
logger = logging.getLogger(__name__)

logger.debug("Debug message")
logger.info("Info message")
logger.error("Error message")
```

### Print debugging (szybkie)

```python
print(f"DEBUG: {variable=}")
```

---

## Środowisko produkcyjne

### Zmienne środowiskowe

```bash
# .env (nie commitować!)
DJANGO_SECRET_KEY=super-secret-key
DJANGO_DEBUG=False
DATABASE_URL=postgres://user:pass@host/db
```

### Konfiguracja (TODO)

1. `python-dotenv` lub `django-environ`
2. Osobne `settings_production.py`
3. Gunicorn jako WSGI server
4. Nginx jako reverse proxy
5. PostgreSQL zamiast SQLite

---

## Przydatne linki

- [Django Documentation](https://docs.djangoproject.com/)
- [Bootstrap 5 Documentation](https://getbootstrap.com/docs/5.3/)
- [PDM Documentation](https://pdm-project.org/)
- [Django Girls Tutorial](https://tutorial.djangogirls.org/)
