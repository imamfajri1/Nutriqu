"""
View untuk dashboard gizi, ringkasan harian, dan laporan mingguan.
"""
import json
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone

from apps.tracking.models import DailyLog, FoodEntry
from apps.tracking.utils import sum_nutrition
from apps.accounts.utils import get_user_tdee, calculate_imt, get_imt_category
from .calculator import get_akg_targets, calculate_progress, get_energy_status


def _get_seven_day_data(user):
    """Ambil data gizi 7 hari terakhir untuk grafik tren."""
    today = timezone.localdate()
    labels = []
    energy_data = []
    protein_data = []

    for i in range(6, -1, -1):
        day = today - timezone.timedelta(days=i)
        labels.append(day.strftime('%d/%m'))

        try:
            log = DailyLog.objects.get(user=user, date=day)
            entries = log.entries.select_related('food__nutritionfact').all()
            total = sum_nutrition(entries)
            energy_data.append(round(total['energy_kcal'], 1))
            protein_data.append(round(total['protein_g'], 1))
        except DailyLog.DoesNotExist:
            energy_data.append(0)
            protein_data.append(0)

    return {
        'labels': labels,
        'energy': energy_data,
        'protein': protein_data,
        'labels_json': json.dumps(labels),
        'energy_json': json.dumps(energy_data),
        'has_nonzero': any(e > 0 for e in energy_data),
    }


@login_required
def dashboard_view(request):
    profile = getattr(request.user, 'profile', None)

    # Wajib ada IMT record untuk akses dashboard penuh
    latest_imt = request.user.imt_records.first()
    has_imt = latest_imt is not None

    imt_value = None
    imt_category = None
    if has_imt:
        imt_value = round(latest_imt.imt, 1)
        imt_category = get_imt_category(imt_value)

    # Ringkasan hari ini
    today = timezone.localdate()
    tdee = get_user_tdee(request.user)

    try:
        log = DailyLog.objects.get(user=request.user, date=today)
        entries = log.entries.select_related('food__nutritionfact').all()
        today_total = sum_nutrition(entries)
    except DailyLog.DoesNotExist:
        today_total = None

    targets = get_akg_targets(profile, tdee) if (profile and tdee) else None
    progress = calculate_progress(today_total, targets) if (today_total and targets) else None
    energy_status = get_energy_status(
        today_total['energy_kcal'] if today_total else 0, tdee or 0
    ) if tdee else None

    # Data grafik 7 hari
    chart_data = _get_seven_day_data(request.user)

    context = {
        'profile': profile,
        'latest_imt': latest_imt,
        'imt_value': imt_value,
        'imt_category': imt_category,
        'has_imt': has_imt,
        'today_total': today_total,
        'targets': targets,
        'progress': progress,
        'energy_status': energy_status,
        'tdee': tdee,
        'chart_data': chart_data,
    }
    return render(request, 'pages/dashboard.html', context)


@login_required
def nutrition_summary_view(request):
    """HTMX partial — ringkasan gizi hari ini."""
    today = timezone.localdate()
    tdee = get_user_tdee(request.user)
    profile = getattr(request.user, 'profile', None)

    try:
        log = DailyLog.objects.get(user=request.user, date=today)
        entries = log.entries.select_related('food__nutritionfact').all()
        today_total = sum_nutrition(entries)
    except DailyLog.DoesNotExist:
        today_total = None

    targets = get_akg_targets(profile, tdee) if (profile and tdee) else None
    progress = calculate_progress(today_total, targets) if (today_total and targets) else None

    context = {
        'today_total': today_total,
        'targets': targets,
        'progress': progress,
        'tdee': tdee,
    }

    if request.htmx:
        return render(request, 'components/nutrition_summary.html', context)
    return render(request, 'pages/dashboard.html', context)


@login_required
def weekly_report_view(request):
    """Laporan mingguan — rata-rata asupan 7 hari terakhir."""
    today = timezone.localdate()
    weekly_data = []
    totals_sum = None

    for i in range(6, -1, -1):
        day = today - timezone.timedelta(days=i)
        try:
            log = DailyLog.objects.get(user=request.user, date=day)
            entries = log.entries.select_related('food__nutritionfact').all()
            day_total = sum_nutrition(entries)
        except DailyLog.DoesNotExist:
            day_total = None

        weekly_data.append({'date': day, 'total': day_total})

    # Hitung rata-rata
    days_with_data = [d for d in weekly_data if d['total']]
    if days_with_data:
        keys = ['energy_kcal', 'protein_g', 'fat_g', 'carbohydrate_g', 'fiber_g']
        count = len(days_with_data)
        average = {k: round(sum(d['total'][k] for d in days_with_data) / count, 1) for k in keys}
    else:
        average = None

    tdee = get_user_tdee(request.user)
    chart_data = _get_seven_day_data(request.user)

    context = {
        'weekly_data': weekly_data,
        'average': average,
        'tdee': tdee,
        'chart_data': chart_data,
    }
    return render(request, 'pages/reports.html', context)
