"""
Kalkulasi nilai gizi per entri makanan berdasarkan jumlah yang dikonsumsi.
Rumus: nilai_aktual = nilai_per_100g × (jumlah_g / 100) × (bdd_pct / 100)
Referensi: TKPI Kemenkes 2020, sheet "Perhitungan Gizi".
"""


def calculate_entry_nutrition(food_entry) -> dict:
    """
    Hitung nilai gizi aktual untuk satu entri makanan.
    Faktor BDD (Bagian Dapat Dimakan) disertakan agar nilai mencerminkan
    porsi yang benar-benar dapat dimakan.
    """
    if not food_entry.food:
        return _empty_nutrition()

    try:
        facts = food_entry.food.nutritionfact
    except Exception:
        return _empty_nutrition()

    bdd = getattr(food_entry.food, 'bdd_pct', 100.0) or 100.0
    factor = (food_entry.amount_g / 100) * (bdd / 100)

    def safe(val):
        return (val or 0) * factor

    return {
        'energy_kcal':        safe(facts.energy_kcal),
        'water_g':            safe(facts.water_g),
        'protein_g':          safe(facts.protein_g),
        'fat_g':              safe(facts.fat_g),
        'carbohydrate_g':     safe(facts.carbohydrate_g),
        'fiber_g':            safe(facts.fiber_g),
        'calcium_mg':         safe(facts.calcium_mg),
        'phosphorus_mg':      safe(facts.phosphorus_mg),
        'iron_mg':            safe(facts.iron_mg),
        'sodium_mg':          safe(facts.sodium_mg),
        'potassium_mg':       safe(facts.potassium_mg),
        'copper_mg':          safe(facts.copper_mg),
        'zinc_mg':            safe(facts.zinc_mg),
        'magnesium_mg':       safe(facts.magnesium_mg),
        'retinol_mcg':        safe(facts.retinol_mcg),
        'beta_carotene_mcg':  safe(facts.beta_carotene_mcg),
        'thiamin_mg':         safe(facts.thiamin_mg),
        'riboflavin_mg':      safe(facts.riboflavin_mg),
        'niacin_mg':          safe(facts.niacin_mg),
        'vitamin_c_mg':       safe(facts.vitamin_c_mg),
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
        'energy_kcal':        0.0,
        'water_g':            0.0,
        'protein_g':          0.0,
        'fat_g':              0.0,
        'carbohydrate_g':     0.0,
        'fiber_g':            0.0,
        'calcium_mg':         0.0,
        'phosphorus_mg':      0.0,
        'iron_mg':            0.0,
        'sodium_mg':          0.0,
        'potassium_mg':       0.0,
        'copper_mg':          0.0,
        'zinc_mg':            0.0,
        'magnesium_mg':       0.0,
        'retinol_mcg':        0.0,
        'beta_carotene_mcg':  0.0,
        'thiamin_mg':         0.0,
        'riboflavin_mg':      0.0,
        'niacin_mg':          0.0,
        'vitamin_c_mg':       0.0,
    }
