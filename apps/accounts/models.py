"""
Model untuk akun pengguna, profil personal, dan riwayat pengukuran IMT.
"""
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

ACTIVITY_CHOICES = [
    ('sedentary', 'Tidak Aktif (kerja kantoran, tidak olahraga)'),
    ('light', 'Ringan (olahraga 1-3x/minggu)'),
    ('moderate', 'Sedang (olahraga 3-5x/minggu)'),
    ('active', 'Aktif (olahraga intensif 6-7x/minggu)'),
    ('very_active', 'Sangat Aktif (atlet / kerja fisik berat)'),
]


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    birth_date = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=[('M', 'Pria'), ('F', 'Wanita')], default='M')
    activity_level = models.CharField(max_length=20, choices=ACTIVITY_CHOICES, default='sedentary')

    class Meta:
        verbose_name = 'Profil Pengguna'
        verbose_name_plural = 'Profil Pengguna'

    def __str__(self):
        return f"Profil {self.user.username}"

    @property
    def is_complete(self):
        """Cek apakah profil sudah lengkap untuk kalkulasi gizi."""
        return bool(self.birth_date and self.gender and self.activity_level)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Buat UserProfile otomatis saat user baru dibuat."""
    if created:
        UserProfile.objects.create(user=instance)


class IMTRecord(models.Model):
    """
    Riwayat pengukuran berat dan tinggi badan.
    Nilai IMT tidak disimpan — dihitung via @property saat dibutuhkan.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='imt_records')
    weight_kg = models.FloatField(verbose_name='Berat Badan (kg)')
    height_cm = models.FloatField(verbose_name='Tinggi Badan (cm)')
    recorded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Catatan IMT'
        verbose_name_plural = 'Catatan IMT'
        ordering = ['-recorded_at']

    def __str__(self):
        return f"{self.user.username} — {self.weight_kg}kg / {self.height_cm}cm ({self.recorded_at.date()})"

    @property
    def imt(self):
        """Hitung Indeks Massa Tubuh: berat(kg) / tinggi(m)²"""
        return self.weight_kg / (self.height_cm / 100) ** 2
