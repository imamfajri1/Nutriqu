"""
Kalkulasi nilai gizi per entri makanan berdasarkan jumlah yang dikonsumsi.
Referensi: semua nilai gizi per 100g, dikalikan faktor porsi.
"""


def calculate_entry_nutrition(food_entry) -> dict:
    """
    Hitung nilai gizi berdasarkan jumlah yang dikonsumsi.
    Semua nilai per 100g → kalikan (amount_g / 100).
    """
    if not food_entry.food:
        return _empty_nutrition()

    try:
        facts = food_entry.food.nutritionfact
    except Exception:
        return _empty_nutrition()

    factor = food_entry.amount_g / 100

    def safe(val):
        return (val or 0) * factor

    return {
        'energy_kcal': safe(facts.energy_kcal),
        'energy_kj': safe(facts.energy_kj),
        'protein_g': safe(facts.protein_g),
        'fat_g': safe(facts.fat_g),
        'carbohydrate_g': safe(facts.carbohydrate_g),
        'fiber_g': safe(facts.fiber_g),
        'calcium_mg': safe(facts.calcium_mg),
        'iron_mg': safe(facts.iron_mg),
        'magnesium_mg': safe(facts.magnesium_mg),
        'thiamin_mg': safe(facts.thiamin_mg),
        'riboflavin_mg': safe(facts.riboflavin_mg),
        'zinc_mg': safe(facts.zinc_mg),
    }


def sum_nutrition(entries) -> dict:
    """Jumlahkan nilai gizi dari semua entri dalam satu log."""
    total = _empty_nutrition()
    for entry in entries:
        entry_nutrition = calculate_entry_nutrition(entry)
        for key in total:
            total[key] += entry_nutrition.get(key, 0)
    return total


def _empty_nutrition() -> dict:
    return {
        'energy_kcal': 0.0,
        'energy_kj': 0.0,
        'protein_g': 0.0,
        'fat_g': 0.0,
        'carbohydrate_g': 0.0,
        'fiber_g': 0.0,
        'calcium_mg': 0.0,
        'iron_mg': 0.0,
        'magnesium_mg': 0.0,
        'thiamin_mg': 0.0,
        'riboflavin_mg': 0.0,
        'zinc_mg': 0.0,
    }
