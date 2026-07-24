"""Moduł do importu przepisów z URL (schema.org) i plików Markdown."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence

import requests
from bs4 import BeautifulSoup


@dataclass
class ParsedIngredient:
    """Sparsowany składnik przepisu."""

    name: str
    amount: float = 0
    unit: str = ""


@dataclass
class ParsedRecipe:
    """Sparsowany przepis gotowy do importu."""

    name: str
    description: str = ""
    instructions: str = ""
    preparation_time: int = 0
    servings: int = 1
    category: str = ""
    ingredients: list[ParsedIngredient] = field(default_factory=list)
    source_url: str = ""


def _parse_iso8601_duration(duration: str) -> int:
    """Parsuje czas w formacie ISO 8601 (PT30M, PT1H30M) na minuty."""
    if not duration:
        return 0

    match = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", duration, re.IGNORECASE)
    if not match:
        return 0

    hours = int(match.group(1) or 0)
    minutes = int(match.group(2) or 0)
    seconds = int(match.group(3) or 0)

    return hours * 60 + minutes + (1 if seconds >= 30 else 0)


def _parse_ingredient_text(text: str) -> ParsedIngredient:
    """Parsuje tekst składnika na strukturę (ilość, jednostka, nazwa)."""
    text = text.strip()
    if not text:
        return ParsedIngredient(name="")

    # Wzorce do rozpoznawania ilości i jednostek
    # Obsługuje: "200g mąki", "2 łyżki cukru", "1/2 szklanki mleka"
    patterns = [
        # "200 g mąki" lub "200g mąki"
        r"^([\d.,/]+)\s*(g|kg|dag|ml|l|szt|łyżk[ai]|łyżeczk[ai]|szklan(?:ka|ki)|szczypta?)\s+(.+)$",
        # "2 jajka" (bez jednostki, ale z liczbą)
        r"^([\d.,/]+)\s+(.+)$",
    ]

    for pattern in patterns:
        match = re.match(pattern, text, re.IGNORECASE)
        if match:
            groups = match.groups()
            if len(groups) == 3:  # ilość, jednostka, nazwa
                amount_str, unit, name = groups
                amount = _parse_amount_string(amount_str)
                unit = _normalize_unit(unit)
                return ParsedIngredient(name=name.strip(), amount=amount, unit=unit)
            elif len(groups) == 2:  # ilość, nazwa (bez jednostki)
                amount_str, name = groups
                amount = _parse_amount_string(amount_str)
                return ParsedIngredient(name=name.strip(), amount=amount, unit="szt")

    # Bez rozpoznanej ilości - cały tekst to nazwa
    return ParsedIngredient(name=text, amount=1, unit="szt")


def _parse_amount_string(amount_str: str) -> float:
    """Parsuje string z ilością na float (obsługuje ułamki jak 1/2)."""
    amount_str = amount_str.strip().replace(",", ".")

    # Obsługa ułamków
    if "/" in amount_str:
        parts = amount_str.split("/")
        if len(parts) == 2:
            try:
                return float(parts[0]) / float(parts[1])
            except ValueError, ZeroDivisionError:
                return 0

    try:
        return float(amount_str)
    except ValueError:
        return 0


def _normalize_unit(unit: str) -> str:
    """Normalizuje jednostkę do standardowej formy."""
    unit = unit.lower().strip()
    unit_map = {
        "g": "g",
        "gram": "g",
        "gramy": "g",
        "gramów": "g",
        "kg": "kg",
        "kilogram": "kg",
        "kilogramy": "kg",
        "dag": "dag",
        "dekagram": "dag",
        "ml": "ml",
        "mililitr": "ml",
        "mililitry": "ml",
        "l": "l",
        "litr": "l",
        "litry": "l",
        "szt": "szt",
        "sztuka": "szt",
        "sztuki": "szt",
        "łyżka": "łyżka",
        "łyżki": "łyżka",
        "łyżeczka": "łyżeczka",
        "łyżeczki": "łyżeczka",
        "szklanka": "szklanka",
        "szklanki": "szklanka",
        "szczypta": "szczypta",
        "szczypty": "szczypta",
    }
    return unit_map.get(unit, unit)


def parse_recipe_from_url(url: str, timeout: int = 10) -> ParsedRecipe:
    """
    Pobiera przepis z URL i parsuje dane schema.org Recipe.

    Args:
        url: URL strony z przepisem
        timeout: Timeout dla żądania HTTP

    Returns:
        ParsedRecipe z danymi przepisu

    Raises:
        ValueError: Gdy nie udało się pobrać lub sparsować przepisu
    """
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

    try:
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
    except requests.RequestException as e:
        raise ValueError(f"Nie udało się pobrać strony: {e}") from e

    soup = BeautifulSoup(response.text, "html.parser")

    # Szukamy danych schema.org w różnych formatach
    recipe_data = None

    # 1. JSON-LD (najczęstszy format)
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(script.string or "")
            recipe_data = _find_recipe_in_jsonld(data)
            if recipe_data:
                break
        except json.JSONDecodeError:
            continue

    # 2. Microdata (alternatywny format)
    if not recipe_data:
        recipe_data = _parse_microdata_recipe(soup)

    if not recipe_data:
        raise ValueError("Nie znaleziono danych przepisu na podanej stronie")

    return _convert_schema_to_parsed_recipe(recipe_data, url)


def _find_recipe_in_jsonld(data: dict | list) -> dict | None:
    """Znajduje obiekt Recipe w strukturze JSON-LD."""
    if isinstance(data, list):
        for item in data:
            result = _find_recipe_in_jsonld(item)
            if result:
                return result
        return None

    if isinstance(data, dict):
        schema_type = data.get("@type", "")
        if isinstance(schema_type, list):
            schema_type = schema_type[0] if schema_type else ""

        if schema_type == "Recipe":
            return data

        # Sprawdź @graph (niektóre strony używają tego formatu)
        if "@graph" in data:
            return _find_recipe_in_jsonld(data["@graph"])

    return None


def _parse_microdata_recipe(soup: BeautifulSoup) -> dict | None:
    """Parsuje przepis z mikrodanych HTML."""
    recipe_el = soup.find(itemtype=re.compile(r"schema\.org/Recipe", re.IGNORECASE))
    if not recipe_el:
        return None

    def get_prop(name: str) -> str:
        el = recipe_el.find(itemprop=name)
        if el:
            return el.get("content", "") or el.get_text(strip=True)
        return ""

    def get_props(name: str) -> list[str]:
        els = recipe_el.find_all(itemprop=name)
        return [el.get("content", "") or el.get_text(strip=True) for el in els]

    return {
        "name": get_prop("name"),
        "description": get_prop("description"),
        "prepTime": get_prop("prepTime"),
        "cookTime": get_prop("cookTime"),
        "totalTime": get_prop("totalTime"),
        "recipeYield": get_prop("recipeYield"),
        "recipeCategory": get_prop("recipeCategory"),
        "recipeIngredient": get_props("recipeIngredient"),
        "recipeInstructions": get_props("recipeInstructions"),
    }


def _convert_schema_to_parsed_recipe(data: dict, url: str) -> ParsedRecipe:
    """Konwertuje dane schema.org na ParsedRecipe."""
    name = data.get("name", "Bez nazwy")
    description = data.get("description", "")

    # Czas przygotowania
    prep_time = _parse_iso8601_duration(data.get("prepTime", ""))
    cook_time = _parse_iso8601_duration(data.get("cookTime", ""))
    total_time = _parse_iso8601_duration(data.get("totalTime", ""))
    preparation_time = total_time or (prep_time + cook_time)

    # Porcje
    yield_str = data.get("recipeYield", "")
    if isinstance(yield_str, list):
        yield_str = yield_str[0] if yield_str else ""
    servings = _extract_number(str(yield_str)) or 1

    # Kategoria
    category = data.get("recipeCategory", "")
    if isinstance(category, list):
        category = category[0] if category else ""

    # Składniki
    ingredients_raw = data.get("recipeIngredient", [])
    if isinstance(ingredients_raw, str):
        ingredients_raw = [ingredients_raw]

    ingredients = [_parse_ingredient_text(ing) for ing in ingredients_raw if ing]

    # Kroki przygotowania (recipeInstructions)
    instructions = _parse_recipe_instructions(data.get("recipeInstructions", []))

    return ParsedRecipe(
        name=name,
        description=description,
        instructions=instructions,
        preparation_time=preparation_time,
        servings=servings,
        category=category,
        ingredients=ingredients,
        source_url=url,
    )


def _parse_recipe_instructions(instructions_data: list | str) -> str:
    """
    Parsuje recipeInstructions ze schema.org na tekst kroków.

    Obsługuje różne formaty:
    - Lista stringów
    - Lista obiektów HowToStep z polem "text"
    - Lista obiektów HowToSection z listą steps
    - Pojedynczy string

    Returns:
        Tekst kroków przygotowania, każdy krok w nowej linii
    """
    if not instructions_data:
        return ""

    if isinstance(instructions_data, str):
        return instructions_data.strip()

    steps: list[str] = []

    for item in instructions_data:
        if isinstance(item, str):
            steps.append(item.strip())
        elif isinstance(item, dict):
            item_type = item.get("@type", "")

            if item_type == "HowToStep" or "text" in item:
                text = item.get("text", "")
                if text:
                    steps.append(text.strip())

            elif item_type == "HowToSection":
                # Sekcja może mieć tytuł i listę kroków
                section_name = item.get("name", "")
                section_steps = item.get("itemListElement", [])

                if section_name:
                    steps.append(f"**{section_name}**")

                for step in section_steps:
                    if isinstance(step, str):
                        steps.append(step.strip())
                    elif isinstance(step, dict):
                        text = step.get("text", "")
                        if text:
                            steps.append(text.strip())

    return "\n".join(steps)


def _extract_number(text: str) -> int:
    """Wyciąga pierwszą liczbę z tekstu."""
    match = re.search(r"\d+", text)
    return int(match.group()) if match else 0


def parse_recipe_from_markdown(content: str) -> ParsedRecipe:
    """
    Parsuje przepis z formatu Markdown.

    Oczekiwany format:
    ```
    # Nazwa przepisu

    Opis przepisu (opcjonalny paragraf po tytule)

    ## Informacje
    - Czas przygotowania: 30 min
    - Porcje: 4
    - Kategoria: obiad

    ## Składniki
    - 200g mąki
    - 2 jajka
    - 1 szklanka mleka

    ## Przygotowanie
    1. Krok pierwszy...
    2. Krok drugi...
    ```

    Args:
        content: Zawartość pliku Markdown

    Returns:
        ParsedRecipe z danymi przepisu
    """
    lines = content.strip().split("\n")

    name = ""
    description = ""
    preparation_time = 0
    servings = 1
    category = ""
    ingredients: list[ParsedIngredient] = []
    instructions_lines: list[str] = []

    current_section = ""
    description_lines: list[str] = []

    for line in lines:
        line_stripped = line.strip()

        # Nagłówek H1 - nazwa przepisu
        if line_stripped.startswith("# ") and not name:
            name = line_stripped[2:].strip()
            current_section = "header"
            continue

        # Nagłówek H2 - sekcja
        if line_stripped.startswith("## "):
            section_name = line_stripped[3:].strip().lower()
            if "informacj" in section_name or "info" in section_name:
                current_section = "info"
            elif "składnik" in section_name or "ingredient" in section_name:
                current_section = "ingredients"
            elif "przygotowanie" in section_name or "instrukcj" in section_name:
                current_section = "instructions"
            else:
                current_section = section_name
            continue

        # Pusta linia
        if not line_stripped:
            continue

        # Przetwarzanie sekcji
        if current_section == "header":
            # Opis - wszystko między tytułem a pierwszą sekcją
            if not line_stripped.startswith("#"):
                description_lines.append(line_stripped)

        elif current_section == "info":
            # Parsowanie informacji
            if ":" in line_stripped:
                key, value = line_stripped.split(":", 1)
                key = key.lower().lstrip("-").strip()
                value = value.strip()

                if "czas" in key:
                    preparation_time = _extract_number(value)
                elif "porcj" in key or "serving" in key:
                    servings = _extract_number(value) or 1
                elif "kategori" in key or "category" in key:
                    category = value

        elif current_section == "ingredients":
            # Parsowanie składników (lista z -)
            if line_stripped.startswith("-") or line_stripped.startswith("*"):
                ingredient_text = line_stripped[1:].strip()
                parsed = _parse_ingredient_text(ingredient_text)
                if parsed.name:
                    ingredients.append(parsed)

        elif current_section == "instructions":
            # Parsowanie kroków przygotowania (numerowana lista lub lista z -)
            if line_stripped:
                # Usuń numer z początku (np. "1. ", "2) ")
                step_text = re.sub(r"^\d+[\.\)]\s*", "", line_stripped)
                # Usuń myślnik/gwiazdkę z początku
                step_text = re.sub(r"^[-*]\s*", "", step_text)
                if step_text:
                    instructions_lines.append(step_text)

    description = " ".join(description_lines).strip()
    instructions = "\n".join(instructions_lines).strip()

    if not name:
        raise ValueError("Nie znaleziono nazwy przepisu (brak nagłówka # na początku)")

    return ParsedRecipe(
        name=name,
        description=description,
        instructions=instructions,
        preparation_time=preparation_time,
        servings=servings,
        category=category,
        ingredients=ingredients,
    )


def validate_parsed_recipe(recipe: ParsedRecipe) -> list[str]:
    """
    Waliduje sparsowany przepis i zwraca listę ostrzeżeń.

    Args:
        recipe: Przepis do walidacji

    Returns:
        Lista ostrzeżeń (pusta jeśli wszystko OK)
    """
    warnings = []

    if not recipe.name:
        warnings.append("Brak nazwy przepisu")

    if not recipe.ingredients:
        warnings.append("Brak składników")

    if recipe.preparation_time == 0:
        warnings.append("Nie rozpoznano czasu przygotowania")

    if recipe.servings <= 0:
        warnings.append("Nieprawidłowa liczba porcji")

    return warnings
