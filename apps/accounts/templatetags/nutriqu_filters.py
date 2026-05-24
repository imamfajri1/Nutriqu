"""
Template filter kustom untuk format angka gaya Indonesia dan kalkulasi persentase.
"""
from django import template

register = template.Library()


@register.filter
def indo_number(value, decimal_places=1):
    """
    Format angka ke gaya Indonesia: koma sebagai desimal, titik sebagai ribuan.
    Contoh: 1234.5 → '1.234,5'
    """
    try:
        value = float(value)
        formatted = f'{value:,.{decimal_places}f}'
        # Ganti separator: koma→X, titik→titik, X→koma
        formatted = formatted.replace(',', 'X').replace('.', ',').replace('X', '.')
        return formatted
    except (TypeError, ValueError):
        return value


@register.filter
def percentage(value, total):
    """Hitung persentase: value / total × 100, kembalikan 0 jika total = 0."""
    try:
        if float(total) == 0:
            return 0
        return round((float(value) / float(total)) * 100, 1)
    except (TypeError, ValueError, ZeroDivisionError):
        return 0


@register.filter
def indo_day(value):
    """Singkatan hari Bahasa Indonesia dari objek date."""
    days = ['SEN', 'SEL', 'RAB', 'KAM', 'JUM', 'SAB', 'MIN']
    try:
        return days[value.weekday()]
    except (AttributeError, IndexError):
        return ''


@register.filter
def progress_color(pct):
    """Tentukan warna progress bar berdasarkan persentase pencapaian target."""
    try:
        pct = float(pct)
    except (TypeError, ValueError):
        return 'gray'

    if pct < 50:
        return 'blue'
    elif pct < 80:
        return 'yellow'
    elif pct <= 110:
        return 'green'
    else:
        return 'red'
