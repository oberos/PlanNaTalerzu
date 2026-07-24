# Projekt aplikacji Django -- Planer posiłków i lista zakupów

## Główne założenia

-   aplikacja dla jednej rodziny
-   dostęp z telefonu i komputera przez przeglądarkę
-   szybkie dodawanie własnych przepisów
-   planowanie obiadów i kolacji
-   automatyczna lista zakupów
-   możliwość oznaczania kupionych produktów
-   brak logowania lub jedno konto administratora

## Architektura

``` text
Django
├── recipes
├── planner
├── shopping
├── inventory (opcjonalnie)
└── nutrition (opcjonalnie)
```

Baza danych: - SQLite (start) - PostgreSQL (docelowo)

## Modele

### Recipe

Przechowuje nazwę, opis, czas przygotowania, liczbę porcji, kategorię i
zdjęcie.

### Ingredient

Przechowuje nazwę składnika, kategorię i domyślną jednostkę.

### RecipeIngredient

Łączy przepis ze składnikiem oraz ilością i jednostką.

### MealPlan

Przechowuje datę, typ posiłku (obiad/kolacja) oraz przypisany przepis.

## Lista zakupów

Generowana dynamicznie: 1. Pobierz wszystkie przepisy z planu. 2. Zsumuj
identyczne składniki. 3. Pogrupuj według kategorii. 4. Wyświetl listę z
możliwością odznaczania zakupionych produktów.

## Widoki

### Dashboard

-   Posiłki na dziś
-   Lista zakupów
-   Najczęściej używane przepisy

### Przepisy

-   wyszukiwanie
-   dodawanie
-   edycja
-   usuwanie

### Szczegóły przepisu

-   zdjęcie
-   składniki
-   instrukcja
-   wartości odżywcze

### Planer

Kalendarz z możliwością przypisywania przepisów do dni oraz drag & drop.

### Lista zakupów

Produkty z checkboxami oznaczającymi zakup.

## Wartości odżywcze

Każdy składnik przechowuje wartości na 100 g: - kcal - białko -
tłuszcz - węglowodany

Aplikacja automatycznie liczy wartości: - dla 100 g przepisu - dla
porcji - dla całego przepisu

## Skalowanie przepisów

Zmiana liczby porcji automatycznie przelicza wszystkie składniki.

## Dodatkowe funkcje

-   kopiowanie tygodniowego planu
-   wyszukiwanie po składnikach, czasie i kaloriach
-   kategorie przepisów
-   filtrowanie ("co ugotować?")
-   import przepisów z linków
-   tryb gotowania krok po kroku

## Funkcje przyszłości

-   historia gotowania
-   ulubione
-   przypomnienia
-   eksport PDF
-   współdzielona lista zakupów
-   integracja z Open Food Facts
-   PWA/offline

## Technologie

-   Django
-   Django REST Framework
-   HTMX
-   Alpine.js
-   Bootstrap 5
-   SQLite / PostgreSQL
-   Gunicorn
-   Nginx

## Spiżarnia

Możliwość oznaczenia produktów znajdujących się w domu. Lista zakupów
uwzględnia tylko brakujące ilości.

## Rozwój

W przyszłości integracja z AI: - generowanie jadłospisu - uwzględnianie
budżetu - liczby osób - limitu kalorii - preferencji żywieniowych
