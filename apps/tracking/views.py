"""
View untuk pencatatan log makanan harian dan food recall.
"""
import json
from datetime import date as date_type, timedelta
from django.db.models import Count
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.contrib import messages
from django.views.decorators.http import require_POST

from .models import DailyLog, FoodEntry, MEAL_CHOICES, MEAL_ORDER
from .utils import sum_nutrition
from apps.foods.models import Food
from apps.accounts.utils import get_user_tdee
from apps.nutrition.calculator import get_akg_targets, calculate_progress, get_energy_status


def _get_or_create_today_log(user):
    today = timezone.localdate()
    log, _ = DailyLog.objects.get_or_create(user=user, date=today)
    return log


def _build_daily_context(user, log):
    """Bangun konteks data untuk tampilan log harian."""
    entries = log.entries.select_related('food', 'food__nutritionfact').all()
    total = sum_nutrition(entries)

    tdee = get_user_tdee(user)
    profile = getattr(user, 'profile', None)
    targets = get_akg_targets(profile, tdee) if (tdee and profile) else None
    progress = calculate_progress(total, targets) if targets else None
    energy_status = get_energy_status(total['energy_kcal'], tdee or 0) if tdee else None

    grouped = {}
    for meal_code, meal_label in MEAL_CHOICES:
        grouped[meal_code] = {
            'label': meal_label,
            'entries': [e for e in entries if e.meal_type == meal_code],
        }

    return {
        'log': log,
        'grouped_entries': grouped,
        'total': total,
        'today_total': total,   # alias agar nutrition_summary.html partial bekerja saat di-include
        'targets': targets,
        'progress': progress,
        'tdee': tdee,
        'energy_status': energy_status,
        'meal_choices': MEAL_CHOICES,
    }


@login_required
def daily_log_view(request):
    today = timezone.localdate()

    date_str = request.GET.get('date')
    try:
        selected_date = date_type.fromisoformat(date_str) if date_str else today
    except (ValueError, TypeError):
        selected_date = today

    log, _ = DailyLog.objects.get_or_create(user=request.user, date=selected_date)
    context = _build_daily_context(request.user, log)

    # Kalender mingguan — mulai Senin minggu ini
    monday = today - timedelta(days=today.weekday())
    week_days = [monday + timedelta(days=i) for i in range(7)]

    logs_with_entries = set(
        DailyLog.objects.filter(user=request.user, date__in=week_days)
        .annotate(entry_count=Count('entries'))
        .filter(entry_count__gt=0)
        .values_list('date', flat=True)
    )

    context.update({
        'selected_date': selected_date,
        'today': today,
        'is_today': selected_date == today,
        'calendar_days': [
            {
                'date': day,
                'has_data': day in logs_with_entries,
                'is_today': day == today,
                'is_selected': day == selected_date,
            }
            for day in week_days
        ],
    })

    if request.htmx:
        return render(request, 'components/nutrition_summary.html', context)
    return render(request, 'pages/log_food.html', context)


@login_required
def add_food_entry_view(request):
    if request.method != 'POST':
        return redirect('daily-log')

    food_id = request.POST.get('food_id')
    custom_name = request.POST.get('custom_name', '').strip()
    meal_type = request.POST.get('meal_type', 'breakfast')
    amount_str = request.POST.get('amount_g', '').strip()

    # Validasi jumlah
    try:
        amount_g = float(amount_str)
        if amount_g <= 0:
            raise ValueError
    except ValueError:
        messages.error(request, 'Jumlah harus berupa angka positif.')
        return redirect('daily-log')

    log = _get_or_create_today_log(request.user)
    food = None

    if food_id:
        food = get_object_or_404(Food, pk=food_id)

    if not food and not custom_name:
        messages.error(request, 'Pilih makanan dari daftar atau masukkan nama kustom.')
        return redirect('daily-log')

    FoodEntry.objects.create(
        log=log,
        food=food,
        custom_name=custom_name if not food else '',
        meal_type=meal_type,
        amount_g=amount_g,
    )
    messages.success(request, 'Makanan berhasil ditambahkan ke log!')

    # Refresh context dan kembalikan partial (HTMX) atau redirect (normal)
    context = _build_daily_context(request.user, log)
    if request.htmx:
        return render(request, 'components/nutrition_summary.html', context)
    return redirect('daily-log')


@login_required
def delete_food_entry_view(request, pk):
    entry = get_object_or_404(FoodEntry, pk=pk, log__user=request.user)

    if request.method in ('POST', 'DELETE'):
        entry.delete()
        messages.success(request, 'Entri berhasil dihapus.')

        log = _get_or_create_today_log(request.user)
        context = _build_daily_context(request.user, log)

        if request.htmx:
            # Kembalikan elemen kosong — HTMX akan swap outerHTML dengan kosong
            return HttpResponse('')
        return redirect('daily-log')

    return redirect('daily-log')


@login_required
@require_POST
def bulk_add_entries_view(request):
    """Terima array item keranjang sebagai JSON dan simpan semuanya ke log hari ini."""
    try:
        payload = json.loads(request.body)
        items = payload.get('items', [])
    except (json.JSONDecodeError, AttributeError):
        return JsonResponse({'ok': False, 'error': 'Payload tidak valid.'}, status=400)

    if not items:
        return JsonResponse({'ok': False, 'error': 'Keranjang kosong.'}, status=400)

    log = _get_or_create_today_log(request.user)
    created_count = 0

    for item in items:
        food_id = item.get('food_id')
        custom_name = str(item.get('custom_name', '')).strip()
        meal_type = item.get('meal_type', 'breakfast')
        try:
            amount_g = float(item.get('amount_g', 0))
            if amount_g <= 0:
                continue
        except (TypeError, ValueError):
            continue

        food = None
        if food_id:
            try:
                food = Food.objects.get(pk=food_id)
            except Food.DoesNotExist:
                pass

        if not food and not custom_name:
            continue

        FoodEntry.objects.create(
            log=log,
            food=food,
            custom_name=custom_name if not food else '',
            meal_type=meal_type,
            amount_g=amount_g,
        )
        created_count += 1

    if created_count == 0:
        return JsonResponse({'ok': False, 'error': 'Tidak ada item valid yang disimpan.'}, status=400)

    return JsonResponse({'ok': True, 'saved': created_count})


@login_required
def food_recall_view(request):
    """Tampilkan asupan kemarin dan opsi salin ke hari ini."""
    yesterday = timezone.localdate() - timezone.timedelta(days=1)

    try:
        yesterday_log = DailyLog.objects.get(user=request.user, date=yesterday)
        entries = yesterday_log.entries.select_related('food').all()
    except DailyLog.DoesNotExist:
        yesterday_log = None
        entries = []

    if request.method == 'POST' and request.POST.get('action') == 'copy':
        # Salin semua entri kemarin ke hari ini
        today_log = _get_or_create_today_log(request.user)
        copied = 0
        for entry in entries:
            FoodEntry.objects.create(
                log=today_log,
                food=entry.food,
                custom_name=entry.custom_name,
                meal_type=entry.meal_type,
                amount_g=entry.amount_g,
            )
            copied += 1
        messages.success(request, f'{copied} entri berhasil disalin ke hari ini!')
        return redirect('daily-log')

    context = {
        'yesterday': yesterday,
        'yesterday_log': yesterday_log,
        'entries': entries,
        'total': sum_nutrition(entries) if entries else None,
    }
    return render(request, 'pages/food_recall.html', context)
