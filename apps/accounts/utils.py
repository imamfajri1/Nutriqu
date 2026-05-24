"""
Kalkulasi IMT, BMR, dan TDEE pengguna.
Referensi: WHO Asia Pasifik (IMT) & Mifflin-St Jeor Equation (BMR).
"""
from datetime import date


ACTIVITY_MULTIPLIERS = {
    'sedentary': 1.2,
    'light': 1.375,
    'moderate': 1.55,
    'active': 1.725,
    'very_active': 1.9,
}


def calculate_imt(weight_kg: float, height_cm: float) -> float:
    """Hitung Indeks Massa Tubuh: berat(kg) / tinggi(m)²"""
    return weight_kg / (height_cm / 100) ** 2


def get_imt_category(imt: float) -> dict:
    """
    Klasifikasi IMT berdasarkan kategori DEPKES RI.
    Mengembalikan dict dengan 'label' dan 'color' untuk tampilan.
    """
    if imt < 17.0:
        return {'label': 'Kurus Berat', 'color': 'blue', 'detail': 'Kurang berat badan tingkat berat'}
    elif imt < 18.5:
        return {'label': 'Kurus Ringan', 'color': 'sky', 'detail': 'Kurang berat badan tingkat ringan'}
    elif imt < 25.0:
        return {'label': 'Normal', 'color': 'green', 'detail': 'Berat badan ideal'}
    elif imt < 27.0:
        return {'label': 'Overweight', 'color': 'yellow', 'detail': 'Kelebihan berat badan'}
    else:
        return {'label': 'Obesitas', 'color': 'red', 'detail': 'Obesitas'}


def calculate_bmr(weight_kg: float, height_cm: float, age: int, gender: str) -> float:
    """
    Hitung Basal Metabolic Rate dengan Mifflin-St Jeor Equation.
    Pria:   (10 × berat) + (6.25 × tinggi) - (5 × usia) + 5
    Wanita: (10 × berat) + (6.25 × tinggi) - (5 × usia) - 161
    """
    base = (10 * weight_kg) + (6.25 * height_cm) - (5 * age)
    return base + 5 if gender == 'M' else base - 161


def calculate_tdee(bmr: float, activity_level: str) -> float:
    """Hitung Total Daily Energy Expenditure berdasarkan level aktivitas."""
    multiplier = ACTIVITY_MULTIPLIERS.get(activity_level, 1.2)
    return bmr * multiplier


def get_user_age(birth_date) -> int:
    """Hitung usia dari tanggal lahir."""
    today = date.today()
    return today.year - birth_date.year - (
        (today.month, today.day) < (birth_date.month, birth_date.day)
    )


def get_user_tdee(user) -> float | None:
    """
    Hitung TDEE untuk user berdasarkan IMT record terkini dan profil.
    Mengembalikan None jika data tidak lengkap.
    """
    profile = getattr(user, 'profile', None)
    if not profile or not profile.is_complete:
        return None

    latest_imt = user.imt_records.first()
    if not latest_imt:
        return None

    age = get_user_age(profile.birth_date)
    bmr = calculate_bmr(latest_imt.weight_kg, latest_imt.height_cm, age, profile.gender)
    return calculate_tdee(bmr, profile.activity_level)
