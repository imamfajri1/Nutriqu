"""
Model untuk pencatatan asupan makanan harian pengguna.
"""
from django.db import models
from django.contrib.auth.models import User

MEAL_CHOICES = [
    ('breakfast', 'Sarapan'),
    ('lunch', 'Makan Siang'),
    ('dinner', 'Makan Malam'),
    ('snack', 'Camilan'),
]

MEAL_ORDER = {'breakfast': 0, 'lunch': 1, 'dinner': 2, 'snack': 3}


class DailyLog(models.Model):
    """Log harian per user — satu record per hari per user."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='daily_logs')
    date = models.DateField(verbose_name='Tanggal')

    class Meta:
        verbose_name = 'Log Harian'
        verbose_name_plural = 'Log Harian'
        unique_together = ('user', 'date')
        ordering = ['-date']

    def __str__(self):
        return f"{self.user.username} — {self.date}"


class FoodEntry(models.Model):
    """Satu entri makanan dalam log harian."""
    log = models.ForeignKey(DailyLog, on_delete=models.CASCADE, related_name='entries')
    food = models.ForeignKey('foods.Food', null=True, blank=True, on_delete=models.SET_NULL)
    custom_name = models.CharField(max_length=200, blank=True, verbose_name='Nama Kustom')
    meal_type = models.CharField(max_length=20, choices=MEAL_CHOICES, verbose_name='Waktu Makan')
    amount_g = models.FloatField(verbose_name='Jumlah (gram)')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Entri Makanan'
        verbose_name_plural = 'Entri Makanan'
        ordering = ['meal_type', 'created_at']

    def __str__(self):
        nama = self.food.name if self.food else self.custom_name
        return f"{nama} — {self.amount_g}g ({self.get_meal_type_display()})"

    @property
    def display_name(self):
        return self.food.name if self.food else self.custom_name
