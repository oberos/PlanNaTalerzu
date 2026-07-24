"""
Konwerter jednostek dla listy zakupów.
Umożliwia sumowanie składników z różnymi jednostkami (np. łyżeczka + ml).
"""

from decimal import Decimal
from typing import NamedTuple


class ConvertedUnit(NamedTuple):
    """Wynik konwersji jednostki."""

    amount: Decimal
    base_unit: str  # ml, g, lub szt


# Jednostki objętości → ml
VOLUME_UNITS = {
    "ml": Decimal("1"),
    "l": Decimal("1000"),
    "łyżka": Decimal("15"),
    "łyżeczka": Decimal("5"),
    "szklanka": Decimal("250"),
}

# Jednostki masy → g
WEIGHT_UNITS = {
    "g": Decimal("1"),
    "kg": Decimal("1000"),
    "dag": Decimal("10"),
    "szczypta": Decimal("0.5"),
}

# Jednostki sztukowe
COUNT_UNITS = {
    "szt": Decimal("1"),
    "sztuka": Decimal("1"),
    "sztuk": Decimal("1"),
}


def normalize_unit(unit: str) -> str:
    """Normalizuj jednostkę (lowercase, strip)."""
    return unit.lower().strip()


def get_base_unit(unit: str) -> str | None:
    """
    Zwraca jednostkę bazową dla danej jednostki.
    ml dla objętości, g dla masy, szt dla sztuk.
    """
    unit = normalize_unit(unit)

    if unit in VOLUME_UNITS:
        return "ml"
    if unit in WEIGHT_UNITS:
        return "g"
    if unit in COUNT_UNITS:
        return "szt"

    return None


def convert_to_base(amount: Decimal, unit: str) -> ConvertedUnit | None:
    """
    Konwertuje ilość do jednostki bazowej.

    Przykłady:
        convert_to_base(2, "łyżeczka") → ConvertedUnit(10, "ml")
        convert_to_base(0.5, "kg") → ConvertedUnit(500, "g")
    """
    unit = normalize_unit(unit)

    if unit in VOLUME_UNITS:
        return ConvertedUnit(amount=amount * VOLUME_UNITS[unit], base_unit="ml")

    if unit in WEIGHT_UNITS:
        return ConvertedUnit(amount=amount * WEIGHT_UNITS[unit], base_unit="g")

    if unit in COUNT_UNITS:
        return ConvertedUnit(amount=amount * COUNT_UNITS[unit], base_unit="szt")

    # Nieznana jednostka - zwróć jako jest (zakładamy sztuki)
    return ConvertedUnit(amount=amount, base_unit=unit or "szt")


def format_amount(amount: Decimal, base_unit: str) -> tuple[str, str]:
    """
    Formatuje ilość w jednostce bazowej do czytelnej formy.

    Przykłady:
        format_amount(1500, "ml") → ("1.5", "l")
        format_amount(50, "ml") → ("50", "ml")
        format_amount(2500, "g") → ("2.5", "kg")
    """
    # Objętość
    if base_unit == "ml":
        if amount >= 1000:
            liters = amount / 1000
            # Zaokrąglij do 2 miejsc po przecinku
            formatted = f"{liters:.2f}".rstrip("0").rstrip(".")
            return (formatted, "l")
        else:
            formatted = f"{amount:.0f}" if amount == int(amount) else f"{amount:.2f}".rstrip("0").rstrip(".")
            return (formatted, "ml")

    # Masa
    if base_unit == "g":
        if amount >= 1000:
            kg = amount / 1000
            formatted = f"{kg:.2f}".rstrip("0").rstrip(".")
            return (formatted, "kg")
        else:
            formatted = f"{amount:.0f}" if amount == int(amount) else f"{amount:.2f}".rstrip("0").rstrip(".")
            return (formatted, "g")

    # Sztuki i inne
    formatted = f"{amount:.0f}" if amount == int(amount) else f"{amount:.2f}".rstrip("0").rstrip(".")
    return (formatted, base_unit)


def aggregate_ingredients(ingredients_data: list[dict]) -> list[dict]:
    """
    Agreguje składniki sumując te same składniki z konwersją jednostek.

    Args:
        ingredients_data: Lista słowników z kluczami:
            - ingredient_id
            - ingredient_name
            - ingredient_category
            - amount (Decimal)
            - unit (str)

    Returns:
        Lista zagregowanych składników z kluczami:
            - ingredient_id
            - ingredient_name
            - ingredient_category
            - display_amount
            - display_unit
            - base_amount
            - base_unit
            - original_entries (lista oryginalnych wpisów)
    """
    # Grupuj po składniku i jednostce bazowej
    aggregated = {}

    for item in ingredients_data:
        ingredient_id = item["ingredient_id"]
        ingredient_name = item["ingredient_name"]
        ingredient_category = item.get("ingredient_category", "")
        amount = Decimal(str(item["amount"]))
        unit = item["unit"]

        converted = convert_to_base(amount, unit)
        if converted is None:
            continue

        key = (ingredient_id, converted.base_unit)

        if key not in aggregated:
            aggregated[key] = {
                "ingredient_id": ingredient_id,
                "ingredient_name": ingredient_name,
                "ingredient_category": ingredient_category,
                "base_amount": Decimal("0"),
                "base_unit": converted.base_unit,
                "original_entries": [],
            }

        aggregated[key]["base_amount"] += converted.amount
        aggregated[key]["original_entries"].append(
            {
                "amount": amount,
                "unit": unit,
            }
        )

    # Formatuj wyniki
    result = []
    for key, data in aggregated.items():
        display_amount, display_unit = format_amount(data["base_amount"], data["base_unit"])

        result.append(
            {
                "ingredient_id": data["ingredient_id"],
                "ingredient_name": data["ingredient_name"],
                "ingredient_category": data["ingredient_category"],
                "display_amount": display_amount,
                "display_unit": display_unit,
                "base_amount": data["base_amount"],
                "base_unit": data["base_unit"],
                "original_entries": data["original_entries"],
            }
        )

    # Sortuj po kategorii, potem nazwie
    result.sort(key=lambda x: (x["ingredient_category"] or "zzz", x["ingredient_name"]))

    return result
