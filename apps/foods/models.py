"""
Model untuk database makanan Indonesia dan nilai gizinya.
Sumber data: TKPI Kemenkes 2020 (Tabel Komposisi Pangan Indonesia 2020).
"""
from django.db import models


class Food(models.Model):
    code = models.CharField(max_length=10, unique=True, verbose_name='Kode')
    name = models.CharField(max_length=200, db_index=True, verbose_name='Nama Makanan')
    name_lower = models.CharField(max_length=200, editable=False)
    source = models.CharField(max_length=100, default='TKPI-2020', verbose_name='Sumber Data')
    is_custom = models.BooleanField(default=False, verbose_name='Makanan Kustom')
    bdd_pct = models.FloatField(default=100.0, verbose_name='BDD (%)')

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
    Nilai gizi per 100g BDD (Bagian Dapat Dimakan).
    Perhitungan porsi: nilai_aktual = nilai_per_100g × (jumlah_g/100) × (bdd_pct/100).
    """
    food = models.OneToOneField(Food, on_delete=models.CASCADE, related_name='nutritionfact')

    # Proksimat
    energy_kcal     = models.FloatField(null=True, blank=True, verbose_name='Energi (kkal)')
    water_g         = models.FloatField(null=True, blank=True, verbose_name='Air (g)')
    protein_g       = models.FloatField(null=True, blank=True, verbose_name='Protein (g)')
    fat_g           = models.FloatField(null=True, blank=True, verbose_name='Lemak (g)')
    carbohydrate_g  = models.FloatField(null=True, blank=True, verbose_name='Karbohidrat (g)')
    fiber_g         = models.FloatField(null=True, blank=True, verbose_name='Serat (g)')

    # Mineral
    calcium_mg      = models.FloatField(null=True, blank=True, verbose_name='Kalsium (mg)')
    phosphorus_mg   = models.FloatField(null=True, blank=True, verbose_name='Fosfor (mg)')
    iron_mg         = models.FloatField(null=True, blank=True, verbose_name='Besi (mg)')
    sodium_mg       = models.FloatField(null=True, blank=True, verbose_name='Natrium (mg)')
    potassium_mg    = models.FloatField(null=True, blank=True, verbose_name='Kalium (mg)')
    copper_mg       = models.FloatField(null=True, blank=True, verbose_name='Tembaga (mg)')
    zinc_mg         = models.FloatField(null=True, blank=True, verbose_name='Seng (mg)')
    magnesium_mg    = models.FloatField(null=True, blank=True, verbose_name='Magnesium (mg)')

    # Vitamin
    retinol_mcg         = models.FloatField(null=True, blank=True, verbose_name='Retinol (mcg)')
    beta_carotene_mcg   = models.FloatField(null=True, blank=True, verbose_name='Beta-Karoten (mcg)')
    thiamin_mg          = models.FloatField(null=True, blank=True, verbose_name='Tiamin (mg)')
    riboflavin_mg       = models.FloatField(null=True, blank=True, verbose_name='Riboflavin (mg)')
    niacin_mg           = models.FloatField(null=True, blank=True, verbose_name='Niasin (mg)')
    vitamin_c_mg        = models.FloatField(null=True, blank=True, verbose_name='Vitamin C (mg)')

    class Meta:
        verbose_name = 'Nilai Gizi'
        verbose_name_plural = 'Nilai Gizi'

    def __str__(self):
        return f"Gizi: {self.food.name}"
