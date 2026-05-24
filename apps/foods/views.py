"""
View untuk pencarian makanan, pemindaian label gizi, dan manajemen database makanan.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db import transaction
from django.core.paginator import Paginator

from .models import Food, NutritionFact
from apps.accounts.utils import ahli_gizi_required


# ── Pencarian (semua user) ──────────────────────────────────────────────────

@login_required
def food_search_view(request):
    q = request.GET.get('q', '').strip()
    foods = []
    if len(q) >= 2:
        foods = Food.objects.filter(name__icontains=q).select_related('nutritionfact')[:10]
    if request.htmx:
        return render(request, 'components/food_search_results.html', {'foods': foods, 'query': q})
    return render(request, 'pages/food_search.html', {'foods': foods, 'query': q})


@login_required
def nutrition_scan_view(request):
    if request.method != 'POST':
        return render(request, 'pages/food_scan.html')
    uploaded_file = request.FILES.get('image')
    if not uploaded_file:
        return JsonResponse({'error': 'Tidak ada file yang diunggah.'}, status=400)
    allowed_types = ['image/jpeg', 'image/png', 'image/webp']
    if uploaded_file.content_type not in allowed_types:
        return JsonResponse({'error': 'Format file tidak didukung. Gunakan JPG atau PNG.'}, status=400)
    if uploaded_file.size > 5 * 1024 * 1024:
        return JsonResponse({'error': 'Ukuran file melebihi 5 MB.'}, status=400)
    try:
        import pytesseract
        from PIL import Image
        import io
        image_data = uploaded_file.read()
        image = Image.open(io.BytesIO(image_data))
        text = pytesseract.image_to_string(image, lang='ind+eng')
        result = _parse_nutrition_label(text)
        return JsonResponse({'success': True, 'data': result})
    except Exception as e:
        return JsonResponse({'error': f'Gagal memproses gambar: {str(e)}'}, status=500)


def _parse_nutrition_label(text: str) -> dict:
    import re
    def find_value(pattern):
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                return float(match.group(1).replace(',', '.'))
            except (ValueError, IndexError):
                return None
        return None
    return {
        'energy_kcal': find_value(r'energi.*?(\d+[,.]?\d*)\s*kkal'),
        'protein_g': find_value(r'protein.*?(\d+[,.]?\d*)\s*g'),
        'fat_g': find_value(r'lemak.*?(\d+[,.]?\d*)\s*g'),
        'carbohydrate_g': find_value(r'karbohidrat.*?(\d+[,.]?\d*)\s*g'),
    }


# ── Manajemen Makanan (ahli gizi / superuser only) ─────────────────────────

def _get_float(post, key):
    """Ambil float dari POST; kembalikan None jika kosong/invalid."""
    val = post.get(key, '').strip()
    if not val:
        return None
    try:
        return float(val.replace(',', '.'))
    except ValueError:
        return None


_NF_FIELDS = [
    'energy_kcal', 'water_g', 'protein_g', 'fat_g', 'carbohydrate_g', 'fiber_g',
    'calcium_mg', 'phosphorus_mg', 'iron_mg', 'sodium_mg', 'potassium_mg',
    'copper_mg', 'zinc_mg', 'magnesium_mg',
    'retinol_mcg', 'beta_carotene_mcg', 'thiamin_mg', 'riboflavin_mg',
    'niacin_mg', 'vitamin_c_mg',
]


def _form_vals(post=None, food=None, facts=None):
    """Pre-resolve semua nilai form sebagai string locale-safe untuk template."""
    def fmt(v):
        if v is None:
            return ''
        return ('%g' % v) if isinstance(v, (int, float)) else str(v).strip()

    if post is not None:
        p = lambda k, d='': post.get(k, '').strip() or d
        vals = {
            'code':    p('code') or fmt(getattr(food, 'code', '')),
            'name':    p('name') or fmt(getattr(food, 'name', '')),
            'source':  p('source', 'Manual'),
            'bdd_pct': p('bdd_pct') or fmt(getattr(food, 'bdd_pct', 100)),
        }
        for field in _NF_FIELDS:
            vals[field] = p(field)
    else:
        vals = {
            'code':    fmt(getattr(food, 'code', '')),
            'name':    fmt(getattr(food, 'name', '')),
            'source':  fmt(getattr(food, 'source', 'Manual')) or 'Manual',
            'bdd_pct': fmt(getattr(food, 'bdd_pct', 100)),
        }
        for field in _NF_FIELDS:
            vals[field] = fmt(getattr(facts, field, None)) if facts else ''
    return vals


@ahli_gizi_required
def food_manage_view(request):
    """Daftar semua makanan dengan search + pagination."""
    q = request.GET.get('q', '').strip()
    qs = Food.objects.select_related('nutritionfact').order_by('name')
    if q:
        qs = qs.filter(name__icontains=q)
    paginator = Paginator(qs, 25)
    page = paginator.get_page(request.GET.get('page'))
    return render(request, 'pages/food_manage.html', {
        'page_obj': page,
        'query': q,
        'total': paginator.count,
    })


@ahli_gizi_required
def food_add_view(request):
    """Tambah makanan baru beserta nilai gizinya."""
    if request.method == 'POST':
        errors = {}
        code = request.POST.get('code', '').strip().upper()
        name = request.POST.get('name', '').strip()

        if not code:
            errors['code'] = 'Kode wajib diisi.'
        elif Food.objects.filter(code=code).exists():
            errors['code'] = f'Kode "{code}" sudah digunakan.'
        if not name:
            errors['name'] = 'Nama makanan wajib diisi.'

        if not errors:
            with transaction.atomic():
                food = Food.objects.create(
                    code=code,
                    name=name,
                    source=request.POST.get('source', 'Manual').strip() or 'Manual',
                    bdd_pct=_get_float(request.POST, 'bdd_pct') or 100.0,
                    is_custom=True,
                )
                NutritionFact.objects.create(
                    food=food,
                    energy_kcal=_get_float(request.POST, 'energy_kcal'),
                    water_g=_get_float(request.POST, 'water_g'),
                    protein_g=_get_float(request.POST, 'protein_g'),
                    fat_g=_get_float(request.POST, 'fat_g'),
                    carbohydrate_g=_get_float(request.POST, 'carbohydrate_g'),
                    fiber_g=_get_float(request.POST, 'fiber_g'),
                    calcium_mg=_get_float(request.POST, 'calcium_mg'),
                    phosphorus_mg=_get_float(request.POST, 'phosphorus_mg'),
                    iron_mg=_get_float(request.POST, 'iron_mg'),
                    sodium_mg=_get_float(request.POST, 'sodium_mg'),
                    potassium_mg=_get_float(request.POST, 'potassium_mg'),
                    copper_mg=_get_float(request.POST, 'copper_mg'),
                    zinc_mg=_get_float(request.POST, 'zinc_mg'),
                    magnesium_mg=_get_float(request.POST, 'magnesium_mg'),
                    retinol_mcg=_get_float(request.POST, 'retinol_mcg'),
                    beta_carotene_mcg=_get_float(request.POST, 'beta_carotene_mcg'),
                    thiamin_mg=_get_float(request.POST, 'thiamin_mg'),
                    riboflavin_mg=_get_float(request.POST, 'riboflavin_mg'),
                    niacin_mg=_get_float(request.POST, 'niacin_mg'),
                    vitamin_c_mg=_get_float(request.POST, 'vitamin_c_mg'),
                )
            messages.success(request, f'Makanan "{name}" berhasil ditambahkan.')
            return redirect('food-manage')
        return render(request, 'pages/food_form.html', {
            'errors': errors, 'action': 'add', 'food': None,
            'v': _form_vals(post=request.POST),
        })

    return render(request, 'pages/food_form.html', {
        'action': 'add', 'food': None, 'errors': {},
        'v': _form_vals(),
    })


@ahli_gizi_required
def food_edit_view(request, pk):
    """Edit data makanan dan nilai gizinya."""
    food = get_object_or_404(Food, pk=pk)
    facts = getattr(food, 'nutritionfact', None)

    if request.method == 'POST':
        errors = {}
        code = request.POST.get('code', '').strip().upper()
        name = request.POST.get('name', '').strip()

        if not code:
            errors['code'] = 'Kode wajib diisi.'
        elif Food.objects.filter(code=code).exclude(pk=pk).exists():
            errors['code'] = f'Kode "{code}" sudah digunakan.'
        if not name:
            errors['name'] = 'Nama makanan wajib diisi.'

        if not errors:
            with transaction.atomic():
                food.code = code
                food.name = name
                food.source = request.POST.get('source', food.source).strip() or food.source
                food.bdd_pct = _get_float(request.POST, 'bdd_pct') or 100.0
                food.save()

                nf_data = dict(
                    energy_kcal=_get_float(request.POST, 'energy_kcal'),
                    water_g=_get_float(request.POST, 'water_g'),
                    protein_g=_get_float(request.POST, 'protein_g'),
                    fat_g=_get_float(request.POST, 'fat_g'),
                    carbohydrate_g=_get_float(request.POST, 'carbohydrate_g'),
                    fiber_g=_get_float(request.POST, 'fiber_g'),
                    calcium_mg=_get_float(request.POST, 'calcium_mg'),
                    phosphorus_mg=_get_float(request.POST, 'phosphorus_mg'),
                    iron_mg=_get_float(request.POST, 'iron_mg'),
                    sodium_mg=_get_float(request.POST, 'sodium_mg'),
                    potassium_mg=_get_float(request.POST, 'potassium_mg'),
                    copper_mg=_get_float(request.POST, 'copper_mg'),
                    zinc_mg=_get_float(request.POST, 'zinc_mg'),
                    magnesium_mg=_get_float(request.POST, 'magnesium_mg'),
                    retinol_mcg=_get_float(request.POST, 'retinol_mcg'),
                    beta_carotene_mcg=_get_float(request.POST, 'beta_carotene_mcg'),
                    thiamin_mg=_get_float(request.POST, 'thiamin_mg'),
                    riboflavin_mg=_get_float(request.POST, 'riboflavin_mg'),
                    niacin_mg=_get_float(request.POST, 'niacin_mg'),
                    vitamin_c_mg=_get_float(request.POST, 'vitamin_c_mg'),
                )
                if facts:
                    for attr, val in nf_data.items():
                        setattr(facts, attr, val)
                    facts.save()
                else:
                    NutritionFact.objects.create(food=food, **nf_data)

            messages.success(request, f'Makanan "{name}" berhasil diperbarui.')
            return redirect('food-manage')
        return render(request, 'pages/food_form.html', {
            'errors': errors, 'action': 'edit', 'food': food,
            'v': _form_vals(post=request.POST, food=food),
        })

    return render(request, 'pages/food_form.html', {
        'action': 'edit', 'food': food, 'errors': {},
        'v': _form_vals(food=food, facts=facts),
    })


@ahli_gizi_required
def food_delete_view(request, pk):
    """Hapus makanan (POST only)."""
    food = get_object_or_404(Food, pk=pk)
    if request.method == 'POST':
        name = food.name
        food.delete()
        messages.success(request, f'Makanan "{name}" berhasil dihapus.')
        return redirect('food-manage')
    return redirect('food-manage')
