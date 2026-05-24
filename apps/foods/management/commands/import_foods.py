"""
Perintah manajemen untuk mengimpor data makanan dari tkpi_2020.json.
Sumber data: TKPI Kemenkes 2020 (Kementerian Kesehatan RI).
Idempotent: skip jika data sudah ada, atau hapus + import ulang dengan --force.
"""
import json
from pathlib import Path
from django.core.management.base import BaseCommand
from apps.foods.models import Food, NutritionFact


NUTRITION_FIELDS = [
    'water_g', 'energy_kcal', 'protein_g', 'fat_g', 'carbohydrate_g', 'fiber_g',
    'calcium_mg', 'phosphorus_mg', 'iron_mg', 'sodium_mg', 'potassium_mg',
    'copper_mg', 'zinc_mg', 'retinol_mcg', 'beta_carotene_mcg',
    'thiamin_mg', 'riboflavin_mg', 'niacin_mg', 'vitamin_c_mg',
]


class Command(BaseCommand):
    help = 'Import data makanan dari data/tkpi_2020.json (TKPI Kemenkes 2020)'

    def add_arguments(self, parser):
        parser.add_argument(
            'file',
            nargs='?',
            default=None,
            help='Path ke file JSON (default: data/tkpi_2020.json di root proyek)',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Paksa reimport meski data TKPI sudah ada di database',
        )

    def handle(self, *args, **options):
        # Skip jika data TKPI sudah ada (idempotent untuk production deploy)
        if not options['force'] and Food.objects.filter(code='AR001').exists():
            self.stdout.write(self.style.WARNING(
                'Data TKPI 2020 sudah ada di database. '
                'Gunakan --force untuk reimport.'
            ))
            return

        if options['file']:
            json_path = Path(options['file'])
        else:
            base_dir = Path(__file__).resolve().parent.parent.parent.parent.parent
            candidates = [
                base_dir / 'data' / 'tkpi_2020.json',
                base_dir / 'tkpi_2020.json',
            ]
            json_path = next((p for p in candidates if p.exists()), None)

        if not json_path or not json_path.exists():
            self.stderr.write(self.style.ERROR(
                'File tkpi_2020.json tidak ditemukan. '
                'Pastikan file ada di folder data/ di root proyek.'
            ))
            return

        self.stdout.write(f'Membaca data dari {json_path}...')

        with open(json_path, encoding='utf-8') as f:
            data = json.load(f)

        foods_data = data.get('foods', [])

        # Hapus semua makanan non-custom beserta nilai gizinya
        deleted = Food.objects.filter(is_custom=False).count()
        Food.objects.filter(is_custom=False).delete()
        self.stdout.write(f'Menghapus {deleted} data lama...')

        imported = 0
        skipped = 0

        for item in foods_data:
            code = item.get('code', '').strip()
            name = item.get('name', '').strip()

            if not code or not name:
                skipped += 1
                continue

            food = Food.objects.create(
                code=code,
                name=name,
                source=item.get('source', 'TKPI-2020'),
                is_custom=False,
                bdd_pct=item.get('bdd_pct') or 100.0,
            )

            NutritionFact.objects.create(
                food=food,
                **{field: item.get(field) for field in NUTRITION_FIELDS}
            )
            imported += 1

        self.stdout.write(self.style.SUCCESS(
            f'Selesai! Imported {imported} makanan dari TKPI 2020. '
            f'{skipped} item dilewati (kosong/tidak valid).'
        ))
