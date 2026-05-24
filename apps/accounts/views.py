"""
View untuk autentikasi pengguna, profil, dan pencatatan IMT.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils import timezone

from .models import UserProfile, IMTRecord, ACTIVITY_CHOICES, ROLE_CHOICES
from .utils import calculate_imt, get_imt_category, calculate_bmr, calculate_tdee


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')

        errors = {}
        if not username:
            errors['username'] = 'Username wajib diisi.'
        elif User.objects.filter(username=username).exists():
            errors['username'] = 'Username sudah digunakan.'
        if not email:
            errors['email'] = 'Email wajib diisi.'
        if len(password1) < 8:
            errors['password1'] = 'Password minimal 8 karakter.'
        if password1 != password2:
            errors['password2'] = 'Password tidak sama.'

        role = request.POST.get('role', 'user')
        if role not in dict(ROLE_CHOICES):
            role = 'user'

        if not errors:
            user = User.objects.create_user(username=username, email=email, password=password1)
            user.profile.role = role
            user.profile.save()
            login(request, user)
            messages.success(request, 'Akun berhasil dibuat! Lengkapi profil kamu dulu ya.')
            return redirect('profile')

        return render(request, 'pages/register.html', {'errors': errors, 'data': request.POST, 'role_choices': ROLE_CHOICES})

    return render(request, 'pages/register.html', {'role_choices': ROLE_CHOICES})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            next_url = request.GET.get('next', 'dashboard')
            return redirect(next_url)
        else:
            return render(request, 'pages/login.html', {
                'error': 'Username atau password salah.',
                'username': username,
            })

    return render(request, 'pages/login.html')


@login_required
def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def profile_view(request):
    profile = request.user.profile
    imt_records = request.user.imt_records.all()[:10]

    if request.method == 'POST':
        birth_date = request.POST.get('birth_date')
        gender = request.POST.get('gender')
        activity_level = request.POST.get('activity_level')

        if birth_date and gender and activity_level:
            profile.birth_date = birth_date
            profile.gender = gender
            profile.activity_level = activity_level
            profile.save()
            messages.success(request, 'Profil berhasil diperbarui!')
            return redirect('profile')
        else:
            messages.error(request, 'Ups, semua field wajib diisi.')

    context = {
        'profile': profile,
        'imt_records': imt_records,
        'activity_choices': ACTIVITY_CHOICES,
    }
    return render(request, 'pages/profile.html', context)


@login_required
def imt_create_view(request):
    if request.method == 'POST':
        try:
            weight_kg = float(request.POST.get('weight_kg', 0))
            height_cm = float(request.POST.get('height_cm', 0))
        except ValueError:
            messages.error(request, 'Berat dan tinggi harus berupa angka.')
            return redirect('imt-add')

        if not (10 <= weight_kg <= 300):
            messages.error(request, 'Berat badan harus antara 10 dan 300 kg.')
            return redirect('imt-add')
        if not (50 <= height_cm <= 250):
            messages.error(request, 'Tinggi badan harus antara 50 dan 250 cm.')
            return redirect('imt-add')

        IMTRecord.objects.create(
            user=request.user,
            weight_kg=weight_kg,
            height_cm=height_cm,
        )
        messages.success(request, 'Data berat dan tinggi badan berhasil disimpan!')
        return redirect('profile')

    latest = request.user.imt_records.first()
    return render(request, 'pages/imt_form.html', {'latest': latest})
