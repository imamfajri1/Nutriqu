"""
View untuk pencarian makanan dan pemindaian label gizi via OCR.
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Food


@login_required
def food_search_view(request):
    """
    HTMX endpoint pencarian makanan.
    GET /makanan/cari/?q=nasi → kembalikan partial template daftar hasil.
    """
    q = request.GET.get('q', '').strip()
    foods = []

    if len(q) >= 2:
        foods = Food.objects.filter(name__icontains=q).select_related('nutritionfact')[:10]

    if request.htmx:
        return render(request, 'components/food_search_results.html', {'foods': foods, 'query': q})

    return render(request, 'pages/food_search.html', {'foods': foods, 'query': q})


@login_required
def nutrition_scan_view(request):
    """
    OCR label gizi dari foto makanan kemasan.
    File diproses in-memory — tidak disimpan ke disk maupun database.
    """
    if request.method != 'POST':
        return render(request, 'pages/food_scan.html')

    uploaded_file = request.FILES.get('image')
    if not uploaded_file:
        return JsonResponse({'error': 'Tidak ada file yang diunggah.'}, status=400)

    # Validasi tipe MIME
    allowed_types = ['image/jpeg', 'image/png', 'image/webp']
    if uploaded_file.content_type not in allowed_types:
        return JsonResponse({'error': 'Format file tidak didukung. Gunakan JPG atau PNG.'}, status=400)

    # Validasi ukuran (maks 5 MB)
    if uploaded_file.size > 5 * 1024 * 1024:
        return JsonResponse({'error': 'Ukuran file melebihi 5 MB.'}, status=400)

    try:
        import pytesseract
        from PIL import Image
        import io
        import re

        image_data = uploaded_file.read()
        image = Image.open(io.BytesIO(image_data))
        text = pytesseract.image_to_string(image, lang='ind+eng')

        # Parser sederhana: cari angka setelah kata kunci gizi
        result = _parse_nutrition_label(text)
        return JsonResponse({'success': True, 'data': result})

    except Exception as e:
        return JsonResponse({'error': f'Gagal memproses gambar: {str(e)}'}, status=500)


def _parse_nutrition_label(text: str) -> dict:
    """Ekstrak nilai gizi dari teks OCR menggunakan regex."""
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
