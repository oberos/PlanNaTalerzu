# Architektura projektu PlanNaTalerzu

## Przegląd

PlanNaTalerzu to aplikacja Django do planowania posiłków i zarządzania listą zakupów dla rodziny. Aplikacja umożliwia tworzenie przepisów ze składnikami, planowanie posiłków na cały tydzień oraz automatyczne generowanie listy zakupów.

## Stack technologiczny

- **Backend**: Django 6.0.7
- **Frontend**: Bootstrap 5.3.3 (CDN)
- **Baza danych**: SQLite (rozwój), planowane PostgreSQL (produkcja)
- **Python**: 3.14.x
- **Zarządzanie zależnościami**: PDM
- **Przetwarzanie obrazów**: Pillow 12.3.0

## Struktura projektu

```
PlanNaTalerzu/
├── pyproject.toml           # Konfiguracja PDM i zależności
├── README.md                # Instrukcja uruchomienia
├── docs/                    # Dokumentacja projektu
│   └── project.md           # Specyfikacja funkcjonalna
├── plannatalerzu/           # Główny katalog Django
│   ├── manage.py            # Skrypt zarządzania Django
│   ├── db.sqlite3           # Baza danych SQLite
│   ├── plannatalerzu/       # Moduł konfiguracyjny Django
│   │   ├── settings.py      # Ustawienia projektu
│   │   ├── urls.py          # Główny routing URL
│   │   ├── views.py         # Widok strony głównej
│   │   ├── wsgi.py          # Konfiguracja WSGI
│   │   └── asgi.py          # Konfiguracja ASGI
│   ├── recipes/             # Aplikacja przepisów
│   ├── planner/             # Aplikacja planowania
│   ├── shopping/            # Aplikacja listy zakupów
│   └── templates/           # Globalne szablony
│       ├── base.html        # Szablon bazowy
│       └── home.html        # Strona główna
```

## Aplikacje Django

### 1. recipes (Przepisy)

Zarządza przepisami i składnikami.

**Modele:**
- `Recipe` - przepis z nazwą, opisem, czasem przygotowania, porcjami, kategorią i zdjęciem
- `Ingredient` - składnik z nazwą, kategorią i domyślną jednostką
- `RecipeIngredient` - relacja łącząca przepis ze składnikiem (ilość, jednostka)

**Funkcjonalności:**
- Tworzenie, edycja, usuwanie przepisów
- Dodawanie istniejących i nowych składników do przepisów
- Dynamiczne dodawanie wierszy składników (JavaScript)

### 2. planner (Planowanie)

Zarządza planami posiłków.

**Modele:**
- `MealPlan` - plan na konkretny dzień z obiadem, kolacją i alternatywą

**Funkcjonalności:**
- Tworzenie nowych planów tygodniowych
- Przypisywanie przepisów do dni tygodnia
- Edycja i usuwanie planów
- Podgląd szczegółów przepisu w modalu

### 3. shopping (Lista zakupów)

Generuje listę zakupów z planów posiłków.

**Status:** Szkielet aplikacji, logika do implementacji.

**Planowane funkcjonalności:**
- Agregacja składników z wybranych planów
- Grupowanie po kategoriach
- Oznaczanie kupionych produktów

## Routing URL

| Ścieżka | Widok | Opis |
|---------|-------|------|
| `/` | `home` | Strona główna |
| `/admin/` | Django Admin | Panel administracyjny |
| `/recipes/` | `recipe_index` | Lista przepisów i formularz dodawania |
| `/planner/` | `planner_index` | Lista planów i zarządzanie |
| `/shopping/` | `shopping_index` | Lista zakupów |

## Szablony

Projekt używa dziedziczenia szablonów Django z Bootstrap 5:

1. **base.html** - szablon bazowy z:
   - Nawigacją (Planowanie, Przepisy, Lista zakupów)
   - Responsywnym menu (hamburger na mobile)
   - Blokami `title` i `content`

2. **Szablony aplikacji** rozszerzają `base.html`

## Konfiguracja

### Ustawienia kluczowe (settings.py)

- `DEBUG = True` - tryb deweloperski
- `ALLOWED_HOSTS` - localhost tylko
- `TEMPLATES.DIRS` - globalny folder templates
- `APP_DIRS = True` - szablony w aplikacjach

### Baza danych

Obecnie SQLite (`db.sqlite3`). Docelowo PostgreSQL.

## Diagram przepływu danych

```
┌─────────────┐     ┌──────────────┐     ┌───────────────┐
│   Recipes   │────►│   Planner    │────►│   Shopping    │
│  (przepisy) │     │(plan posiłków)│    │(lista zakupów)│
└─────────────┘     └──────────────┘     └───────────────┘
       │                   │                     │
       ▼                   ▼                     ▼
┌─────────────┐     ┌──────────────┐     ┌───────────────┐
│ Recipe      │     │ MealPlan     │     │ (do implem.)  │
│ Ingredient  │     │              │     │               │
│ RecipeIngr. │     │              │     │               │
└─────────────┘     └──────────────┘     └───────────────┘
```

## Bezpieczeństwo

- CSRF protection włączony
- XFrame options middleware
- Session-based authentication (opcjonalnie)
- **UWAGA**: SECRET_KEY w settings.py jest jawny - zmienić na produkcji!
