"""
Perintah manajemen untuk mengimpor data makanan dari nutrisurvey_indo.json ke database.
Idempotent: lewati makanan yang sudah ada berdasarkan kode.
"""
import json
from pathlib import Path
from django.core.management.base import BaseCommand
from apps.foods.models import Food, NutritionFact


class Command(BaseCommand):
    help = 'Import data makanan dari file nutrisurvey_indo.json'

    def add_arguments(self, parser):
        parser.add_argument(
            'file',
            nargs='?',
            default=None,
            help='Path ke file JSON (default: cari di root proyek)',
        )

    def handle(self, *args, **options):
        # Cari file JSON di root proyek jika tidak diberikan argumen
        if options['file']:
            json_path = Path(options['file'])
        else:
            base_dir = Path(__file__).resolve().parent.parent.parent.parent.parent
            candidates = [
                base_dir / 'data' / 'nutrisurvey_indo.json',
                base_dir / 'nutrisurvey_indo.json',
            ]
            json_path = next((p for p in candidates if p.exists()), None)

        if not json_path or not json_path.exists():
            self.stderr.write(self.style.ERROR(
                'File nutrisurvey_indo.json tidak ditemukan. '
                'Taruh di folder data/ atau berikan path sebagai argumen.'
            ))
            return

        self.stdout.write(f'Membaca data dari {json_path}...')

        with open(json_path, encoding='utf-8') as f:
            data = json.load(f)

        foods_data = data.get('foods', [])
        imported = 0
        skipped = 0

        for item in foods_data:
            code = item.get('id', '').strip()
            name = item.get('name', '').strip()

            if not code or not name:
                continue

            food, created = Food.objects.get_or_create(
                code=code,
                defaults={
                    'name': name,
                    'source': 'DKBM-Nutrisurvey',
                },
            )

            if not created:
                skipped += 1
                continue

            NutritionFact.objects.create(
                food=food,
                energy_kcal=item.get('energy_kcal'),
                energy_kj=item.get('energy_kj'),
                protein_g=item.get('protein_g'),
                fat_g=item.get('fat_g'),
                carbohydrate_g=item.get('carbohydrate_g'),
                fiber_g=item.get('fiber_g'),
                calcium_mg=item.get('calcium_mg'),
                iron_mg=item.get('iron_mg'),
                magnesium_mg=item.get('magnesium_mg'),
                thiamin_mg=item.get('thiamin_mg'),
                riboflavin_mg=item.get('riboflavin_mg'),
                zinc_mg=item.get('zinc_mg'),
            )
            imported += 1

        self.stdout.write(self.style.SUCCESS(
            f'Selesai! Imported {imported} makanan baru. {skipped} sudah ada, dilewati.'
        ))
