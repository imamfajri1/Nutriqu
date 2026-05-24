"""
Kalkulasi target AKG (Angka Kecukupan Gizi) harian.
Referensi: Permenkes No.28 Tahun 2019 tentang AKG Indonesia.
"""
from apps.accounts.utils import get_user_age


def get_akg_targets(user_profile, tdee: float) -> dict:
    """
    Hitung target gizi harian berdasarkan TDEE dan profil pengguna.
    Distribusi makro mengikuti AKG Indonesia (Permenkes 28/2019):
      - Protein      : 10-15% energi → (tdee × 0.13) / 4
      - Lemak        : 20-30% energi → (tdee × 0.25) / 9
      - Karbohidrat  : 50-65% energi → (tdee × 0.575) / 4
    Mikronutrien menggunakan nilai flat AKG dewasa (19-29 tahun).
    """
    gender_m = user_profile.gender == 'M'

    return {
        # Makronutrien berbasis TDEE
        'energy_kcal':    tdee,
        'protein_g':      (tdee * 0.13) / 4,
        'fat_g':          (tdee * 0.25) / 9,
        'carbohydrate_g': (tdee * 0.575) / 4,
        'fiber_g':        _get_fiber_target(user_profile),

        # Mineral (AKG 2019)
        'calcium_mg':     1000.0,
        'phosphorus_mg':  700.0,
        'iron_mg':        11.0 if gender_m else 26.0,
        'sodium_mg':      1500.0,
        'potassium_mg':   4700.0,
        'copper_mg':      0.9,
        'zinc_mg':        11.0 if gender_m else 8.0,

        # Vitamin (AKG 2019)
        'retinol_mcg':    650.0 if gender_m else 600.0,
        'thiamin_mg':     1.2 if gender_m else 1.1,
        'riboflavin_mg':  1.3 if gender_m else 1.1,
        'niacin_mg':      16.0 if gender_m else 14.0,
        'vitamin_c_mg':   90.0 if gender_m else 75.0,
    }


def _get_fiber_target(user_profile) -> float:
    """Target serat harian berdasarkan usia dan jenis kelamin (AKG 2019)."""
    if not user_profile.birth_date:
        return 25.0

    age = get_user_age(user_profile.birth_date)

    if age < 18:
        return 25.0
    elif age <= 64:
        return 30.0 if user_profile.gender == 'M' else 25.0
    else:
        return 28.0 if user_profile.gender == 'M' else 22.0


def calculate_progress(current: dict, target: dict) -> dict:
    """
    Hitung persentase pencapaian target harian.
    Mengembalikan dict dengan key sama + suffix '_pct'.
    """
    result = {}
    for key, target_val in target.items():
        current_val = current.get(key, 0)
        if target_val and target_val > 0:
            pct = min((current_val / target_val) * 100, 150)
        else:
            pct = 0
        result[key] = current_val
        result[f'{key}_pct'] = round(pct, 1)
    return result


def get_energy_status(current_kcal: float, target_kcal: float) -> str:
    """Tentukan status energi: Kurang, Cukup, atau Lebih."""
    if target_kcal <= 0:
        return 'Tidak Diketahui'
    pct = (current_kcal / target_kcal) * 100
    if pct < 80:
        return 'Kurang'
    elif pct <= 110:
        return 'Cukup'
    else:
        return 'Lebih'
