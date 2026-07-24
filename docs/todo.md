# TODO - Funkcjonalności do implementacji

## 🔴 Wysokie priorytet (krytyczne)

### 1. Lista zakupów - generowanie
**Status:** ✅ Zaimplementowane  
**Pliki:** `shopping/views.py`, `shopping/unit_converter.py`, `shopping/templates/shopping/index.html`

**Zrealizowane:**
- [x] Wybór planu do wygenerowania listy (select)
- [x] Agregacja składników z przepisów w planie
- [x] **Konwersja jednostek** (łyżeczka→ml, l→ml, kg→g, itp.)
- [x] Sumowanie ilości identycznych składników
- [x] Automatyczna konwersja do większych jednostek (>1000ml → l, >1000g → kg)
- [x] Grupowanie po kategoriach składników
- [x] Tooltip z rozkładem oryginalnych wpisów (np. "2 łyżeczki + 500ml")

**Obsługiwane jednostki:**
- Objętość: ml, l, łyżka (15ml), łyżeczka (5ml), szklanka (250ml)
- Masa: g, kg, dag, szczypta (0.5g)
- Sztukowe: szt

### 2. Oznaczanie zakupionych produktów
**Status:** ✅ Zaimplementowane (localStorage)

**Zrealizowane:**
- [x] Checkboxy przy każdej pozycji
- [x] Zapis stanu w localStorage (per plan)
- [x] Przekreślanie zakupionych pozycji
- [x] Przyciski "Wyczyść zaznaczenia" i "Zaznacz wszystko"

---

## 🟡 Średni priorytet

### 3. Wyszukiwanie przepisów
**Plik:** `recipes/views.py`, `recipes/index.html`

**Wymagania:**
- [ ] Pole wyszukiwania na liście przepisów
- [ ] Filtrowanie po nazwie, kategorii
- [ ] Filtrowanie po składnikach
- [ ] Filtrowanie po czasie przygotowania

### 4. Kategorie przepisów
**Status:** Pole istnieje, brak UI do zarządzania

**Wymagania:**
- [ ] Predefiniowane kategorie (obiad, kolacja, śniadanie, deser)
- [ ] Select zamiast input w formularzu
- [ ] Filtrowanie po kategorii

### 5. Edycja składników przepisu
**Status:** ✅ Zaimplementowane

**Zrealizowane:**
- [x] Wyświetlanie aktualnych składników podczas edycji
- [x] Możliwość usunięcia składnika z przepisu
- [x] Możliwość dodawania nowych składników przez modal

### 6. Obsługa obrazów przepisów
**Status:** Model gotowy, UI brakuje

**Wymagania:**
- [ ] Upload obrazu w formularzu
- [ ] Wyświetlanie miniaturki na liście
- [ ] Wyświetlanie pełnego obrazu w szczegółach
- [ ] Konfiguracja MEDIA_URL i MEDIA_ROOT

---

## 🟢 Niski priorytet (nice to have)

### 7. Wartości odżywcze
**Status:** ✅ Zaimplementowane

**Zrealizowane:**
- [x] Model `NutritionInfo` dla składników (kalorie, białko, węglowodany, tłuszcze, błonnik na 100g/100ml)
- [x] Kalkulacja dla przepisu (suma składników z konwersją jednostek)
- [x] Przeliczanie na porcję
- [x] Wyświetlanie w szczegółach przepisu (rozwijana sekcja "Pokaż wartości odżywcze")
- [x] Panel admina: inline przy składnikach + osobny widok NutritionInfo
- [x] Informacja o składnikach bez uzupełnionych wartości

**Pliki:**
- `recipes/models.py` - model NutritionInfo, metoda Recipe.calculate_nutrition()
- `recipes/admin.py` - rejestracja NutritionInfoAdmin z inline
- `recipes/templates/recipes/index.html` - UI wartości odżywczych

### 8. Skalowanie przepisów
**Status:** Brak implementacji

**Wymagania:**
- [ ] Możliwość zmiany liczby porcji
- [ ] Automatyczne przeliczenie składników
- [ ] JavaScript do dynamicznego przeliczania

### 9. Kopiowanie planu tygodniowego
**Status:** Brak

**Wymagania:**
- [ ] Przycisk "Kopiuj plan"
- [ ] Tworzenie kopii z nową nazwą
- [ ] Kopiowanie wszystkich przypisań przepisów

### 10. Import przepisów z URL / Markdown
**Status:** ✅ Zaimplementowane

**Zrealizowane:**
- [x] Pole na URL przepisu
- [x] Parsowanie popularnych stron (schema.org Recipe)
- [x] Mapowanie na model Recipe
- [x] Import przepisu z pliku Markdown (.md)
- [x] Parsowanie struktury Markdown (nagłówki, listy składników)
- [x] Przykładowy plik z przepisem przechowywany w repozytorium (`examples/przepis_nalesniki.md`)
- [x] Walidacja i podgląd przed importem

**Pliki:**
- `recipes/import_utils.py` - moduł parsowania URL/Markdown
- `recipes/views.py` - widoki import_preview, import_confirm
- `recipes/urls.py` - nowe endpointy
- `recipes/templates/recipes/index.html` - modal importu

### 11. Tryb gotowania krok po kroku
**Status:** Brak

**Wymagania:**
- [ ] Osobne pole na kroki (JSON lub osobny model)
- [ ] Widok prezentacyjny z dużą czcionką
- [ ] Nawigacja prev/next

### 12. Dashboard
**Status:** Strona główna jest uproszczona

**Planowane:**
- [ ] Posiłki na dziś (z aktualnego planu)
- [ ] Skrócona lista zakupów
- [ ] Najczęściej używane przepisy
- [ ] Statystyki

### 13. Format schema.org Recipe (kroki przygotowania)
**Status:** ✅ Zaimplementowane

**Opis:** Rozszerzenie modelu Recipe o pola kompatybilne z formatem schema.org Recipe, w szczególności dodanie kroków przygotowania (recipeInstructions).

**Zrealizowane:**
- [x] Dodanie pola `instructions` do modelu Recipe (TextField)
- [x] Formularz do dodawania/edycji kroków przygotowania
- [x] Wyświetlanie kroków w szczegółach przepisu (rozwijana lista)
- [x] Kompatybilność z importem schema.org (parsowanie recipeInstructions)
- [x] Parsowanie kroków z Markdown (sekcja ## Przygotowanie)
- [x] Podgląd kroków w modalu importu

**Pliki:**
- `recipes/models.py` - dodano pole `instructions`
- `recipes/import_utils.py` - parsowanie `recipeInstructions` ze schema.org i Markdown
- `recipes/views.py` - obsługa pola w formularzach
- `recipes/templates/recipes/index.html` - UI formularza i wyświetlanie kroków

**Powiązania:**
- Rozszerza funkcjonalność importu (zadanie 10)
- Wymagane do pełnego eksportu przepisów (zadanie 14)
- Powiązane z trybem gotowania (zadanie 11)

### 14. Eksport pojedynczego przepisu
**Status:** Brak

**Opis:** Możliwość eksportu przepisu do formatu Markdown, pdf lub JSON (schema.org Recipe) z poziomu aplikacji.

**Wymagania:**
- [ ] Przycisk "Eksportuj" przy każdym przepisie
- [ ] Wybór formatu eksportu (Markdown / pdf / JSON schema.org)
- [ ] Generowanie pliku do pobrania
- [ ] Eksport do Markdown w formacie kompatybilnym z importem
- [ ] Eksport do JSON-LD zgodnego ze schema.org/Recipe
- [ ] Eksport do pdf do latwego dzielenia sie z innymi ludzmi

---

## 🐛 Znane problemy (bugs)

### B1. ~~Edycja przepisu nie pokazuje aktualnych składników~~ ✅ NAPRAWIONE
**Opis:** Formularz edycji nie wypełnia pól składnikami.  
**Plik:** `recipes/index.html`  
**Priorytet:** ~~Średni~~ Naprawione  
**Rozwiązanie:** Przy edycji przepisu aktualne składniki są wyświetlane jako lista z możliwością usunięcia.

### B2. Brak walidacji formularzy
**Opis:** Brak komunikatów o błędach (np. pusta nazwa).  
**Pliki:** wszystkie views  
**Priorytet:** Niski

### B3. Brak potwierdzenia usunięcia
**Opis:** Usunięcie przepisu/planu bez potwierdzenia.  
**Pliki:** templates  
**Priorytet:** Niski

### B4. SECRET_KEY w settings.py
**Opis:** Klucz jest jawny w kodzie źródłowym.  
**Plik:** `plannatalerzu/settings.py`  
**Rozwiązanie:** Użyć zmiennych środowiskowych  
**Priorytet:** Wysoki (przed produkcją)

### B5. ~~Nie można dodać składnika z poziomu przepisu~~ ✅ NAPRAWIONE
**Opis:** Użytkownik nie jest w stanie dodać składnika podczas tworzenia nowego przepisu.  
**Plik:** `recipes/views.py`, `recipes/index.html`  
**Priorytet:** ~~Wysoki~~ Naprawione  
**Rozwiązanie:** Przeprojektowano UX dodawania składników:
- Przycisk "Dodaj składnik" otwiera modal Bootstrap
- Modal zawiera select z listą składników, pole ilości i select jednostki (g/kg/ml/l/szt/łyżka/łyżeczka/szklanka/szczypta)
- Opcja "Utwórz nowy składnik" pozwala dodać brakujący składnik przez AJAX
- Po dodaniu składnika wraca do modalu z nowym składnikiem na liście
- Dodane składniki wyświetlają się jako lista z przyciskiem usuwania
- Przy edycji przepisu wyświetlane są aktualne składniki

---

## 📋 Backlog techniczny

- [ ] Testy dla shopping app
- [ ] Testy integracyjne E2E
- [ ] Migracja na PostgreSQL
- [ ] Konfiguracja produkcyjna (Gunicorn, nginx)
- [ ] Dockerfile i docker-compose
- [ ] CI/CD pipeline
- [ ] Logi i monitoring
- [ ] Internacjonalizacja (i18n)
- [ ] API REST (Django REST Framework)
- [ ] Progressive Web App (PWA)
