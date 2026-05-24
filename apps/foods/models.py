"""
Model untuk database makanan Indonesia dan nilai gizinya.
Sumber data: DKBM Indonesia via Nutrisurvey (indo.fta).
"""
from django.db import models


class Food(models.Model):
    code = models.CharField(max_length=10, unique=True, verbose_name='Kode')
    name = models.CharField(max_length=200, db_index=True, verbose_name='Nama Makanan')
    name_lower = models.CharField(max_length=200, editable=False)  # untuk pencarian case-insensitive
    source = models.CharField(max_length=100, default='DKBM-Nutrisurvey', verbose_name='Sumber Data')
    is_custom = models.BooleanField(default=False, verbose_name='Makanan Kustom')

    class Meta:
        verbose_name = 'Makanan'
        verbose_name_plural = 'Makanan'
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.name_lower = self.name.lower()
        super().save(*args, **kwargs)


class NutritionFact(models.Model):
    """
    Nilai gizi per 100g bahan makanan.
    Semua perhitungan porsi dilakukan di luar model ini (kalikan dengan faktor porsi).
    """
    food = models.OneToOneField(Food, on_delete=models.CASCADE, related_name='nutritionfact')
    energy_kcal = models.FloatField(null=True, blank=True, verbose_name='Energi (kkal)')
    energy_kj = models.FloatField(null=True, blank=True, verbose_name='Energi (kJ)')
    protein_g = models.FloatField(null=True, blank=True, verbose_name='Protein (g)')
    fat_g = models.FloatField(null=True, blank=True, verbose_name='Lemak (g)')
    carbohydrate_g = models.FloatField(null=True, blank=True, verbose_name='Karbohidrat (g)')
    fiber_g = models.FloatField(null=True, blank=True, verbose_name='Serat (g)')
    calcium_mg = models.FloatField(null=True, blank=True, verbose_name='Kalsium (mg)')
    iron_mg = models.FloatField(null=True, blank=True, verbose_name='Besi (mg)')
    magnesium_mg = models.FloatField(null=True, blank=True, verbose_name='Magnesium (mg)')
    thiamin_mg = models.FloatField(null=True, blank=True, verbose_name='Tiamin (mg)')
    riboflavin_mg = models.FloatField(null=True, blank=True, verbose_name='Riboflavin (mg)')
    zinc_mg = models.FloatField(null=True, blank=True, verbose_name='Zinc (mg)')

    class Meta:
        verbose_name = 'Nilai Gizi'
        verbose_name_plural = 'Nilai Gizi'

    def __str__(self):
        return f"Gizi: {self.food.name}"
