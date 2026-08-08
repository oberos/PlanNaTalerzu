# PlanNaTalerzu

## Uruchamianie projektu lokalnie

### 1. Aktywuj środowisko wirtualne

Jeśli środowisko znajduje się w katalogu `.venv`, uruchom:

```bash
source .venv/bin/activate
```

### 2. Zainstaluj zależności

Jeśli używasz PDM, zainstaluj zależności z pliku projektu:

```bash
pdm install
```

### 3. Uruchom migracje

```bash
python manage.py migrate
```

### 4. Uruchom serwer deweloperski

```bash
python manage.py runserver 8081
```

Po uruchomieniu aplikacja będzie dostępna pod adresem:

```text
http://127.0.0.1:8081/
```

### 5. Tworzenie superużytkownika

Jeśli chcesz zalogować się do panelu administracyjnego Django:

```bash
python manage.py createsuperuser
```

### 6. Wczytanie składników z wartościami odżywczymi

Projekt zawiera gotowy zestaw 111 popularnych składników (mięso, ryby, warzywa, owoce, nabiał, przyprawy, pieczywo i więcej) wraz z wartościami odżywczymi na 100g/100ml.

Aby załadować je do bazy danych:

```bash
python manage.py loaddata ingredients
```

Fixture znajduje się w `recipes/fixtures/ingredients.json`.

### 7. Zrzucanie aktualnych danych przepisów i składników do fixture

Możesz wygenerować aktualny plik fixture JSON z danych bazy dla całego modułu `recipes`:

```bash
python manage.py dump_recipe_fixtures
```

Lub użyj gotowego skryptu repozytorium:

```bash
./dump_recipe_fixtures.sh
```

Domyślny plik wyjściowy to `recipes/fixtures/recipe_data.json`.

Aby załadować ten fixture po odtworzeniu projektu:

```bash
python manage.py loaddata recipes/fixtures/recipe_data.json
```

Lub użyj gotowego skryptu repozytorium:

```bash
./load_recipe_fixtures.sh
```
