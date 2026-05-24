# Nutriqu

Aplikasi web pencatatan gizi harian berbasis data pangan Indonesia. Dirancang untuk membantu pengguna memahami asupan nutrisi mereka secara personal dengan kalkulasi kebutuhan gizi mengikuti standar AKG Permenkes No.28 Tahun 2019.

## Fitur Utama

- **Log Makanan Harian** — Catat asupan per waktu makan (sarapan, makan siang, makan malam, camilan) dengan pencarian real-time dari 937+ data pangan Indonesia
- **Ringkasan Gizi Otomatis** — Kalkulasi energi, protein, lemak, karbohidrat, dan serat dibanding target AKG personal secara live (HTMX)
- **IMT & Riwayat Berat Badan** — Pantau Indeks Massa Tubuh dengan kategori DEPKES RI (Kurus Berat, Kurus Ringan, Normal, Overweight, Obesitas)
- **Food Recall** — Lihat rekap asupan kemarin dan salin ke hari ini dengan satu klik
- **Laporan Mingguan** — Grafik tren kalori 7 hari, rata-rata harian, dan tabel detail per hari
- **Target TDEE Personal** — Kalkulasi TDEE (Total Daily Energy Expenditure) berbasis Mifflin-St Jeor × faktor aktivitas, dikustomisasi per jenis kelamin, usia, dan level aktivitas

## Tangkapan Layar

| Dashboard | Log Makanan | Laporan |
|---|---|---|
| Ringkasan harian + IMT card + grafik tren | Pencarian makanan live + entri per waktu makan | Grafik bar 7 hari + rata-rata makro |

## Teknologi

### Backend
| Teknologi | Versi | Kegunaan |
|---|---|---|
| Python | 3.12 | Runtime |
| Django | 5.2 | Web framework |
| django-htmx | 1.21+ | Middleware HTMX |
| python-decouple | 3.8+ | Manajemen environment variable |
| WhiteNoise | 6.7+ | Serving static files di production |
| psycopg | 3.1+ | Driver PostgreSQL (Supabase) |
| Gunicorn | 22.0+ | WSGI server production |

### Frontend
| Teknologi | Kegunaan |
|---|---|
| Tailwind CSS v3 | Utility-first CSS framework |
| HTMX 2.0.4 | Interaksi partial update tanpa JS custom |
| Alpine.js 3.x | Reaktivitas UI ringan (form state, mobile nav) |
| Chart.js 4.4.4 | Grafik tren kalori dan laporan mingguan |

### Database
- **Development**: SQLite (lokal, zero-config)
- **Production**: PostgreSQL via [Supabase](https://supabase.com)

### Deployment
- **Platform**: [Vercel](https://vercel.com) (Serverless Python)

## Struktur Proyek

```
nutriqu/
├── apps/
│   ├── accounts/       # Autentikasi, UserProfile, IMTRecord
│   ├── foods/          # Model Food, NutritionFact, search view
│   ├── tracking/       # DailyLog, FoodEntry, food recall
│   └── nutrition/      # Dashboard, laporan mingguan, kalkulasi AKG
├── config/
│   ├── settings/
│   │   ├── base.py         # Pengaturan bersama
│   │   ├── development.py  # SQLite + DEBUG=True
│   │   └── production.py   # PostgreSQL + WhiteNoise
│   ├── urls.py
│   └── wsgi.py
├── data/
│   └── nutrisurvey_indo.json   # 937 data pangan Indonesia (DKBM)
├── static/
│   ├── css/main.css            # Tailwind CSS (build lokal)
│   └── js/                     # HTMX, Alpine.js, Chart.js (lokal)
├── templates/
│   ├── base.html
│   ├── components/             # HTMX partials
│   └── pages/                  # Halaman utama
├── tailwind.config.js
├── manage.py
└── requirements.txt
```

## Setup Lokal

### Prasyarat

- Python 3.12+
- Node.js 18+ (untuk build Tailwind CSS)

### 1. Clone dan buat virtual environment

```bash
git clone <repo-url>
cd nutriqu
python -m venv env
```

**Windows (PowerShell):**
```powershell
.\env\Scripts\Activate.ps1
```

**Mac/Linux:**
```bash
source env/bin/activate
```

### 2. Install dependensi Python

```bash
pip install -r requirements-dev.txt
```

### 3. Konfigurasi environment

```bash
cp .env.example .env
```

Edit `.env` dan isi `SECRET_KEY`:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
DJANGO_SETTINGS_MODULE=config.settings.development
```

Generate secret key baru:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 4. Migrasi database dan import data pangan

```bash
python manage.py migrate
python manage.py import_foods
```

Output yang diharapkan: `Imported 937 makanan baru.`

### 5. Build CSS lokal

```bash
npm install
npm run build:css
```

### 6. Buat superuser (opsional)

```bash
python manage.py createsuperuser
```

### 7. Jalankan server development

```bash
python manage.py runserver
```

Buka `http://127.0.0.1:8000` di browser.

## Development Workflow

Saat mengubah template HTML dan menambah class Tailwind baru, rebuild CSS:

```bash
# Sekali
npm run build:css

# Mode watch (auto-rebuild saat ada perubahan)
npm run watch:css
```

## Deployment ke Vercel

### 1. Setup database PostgreSQL (Supabase)

Buat project baru di [Supabase](https://supabase.com), ambil connection string dari **Project Settings → Database → Connection pooling**.

### 2. Konfigurasi environment variable di Vercel

Tambahkan di Vercel Dashboard → Settings → Environment Variables:

```
SECRET_KEY=<secret-key-production>
DEBUG=False
DJANGO_SETTINGS_MODULE=config.settings.production
DB_NAME=postgres
DB_USER=postgres.<project-ref>
DB_PASSWORD=<password>
DB_HOST=aws-0-ap-southeast-1.pooler.supabase.com
DB_PORT=5432
```

### 3. Deploy

```bash
vercel --prod
```

Atau connect repo ke Vercel Dashboard untuk auto-deploy dari branch `main`.

### 4. Jalankan migrasi dan import data di production

```bash
vercel env pull .env.production
DJANGO_SETTINGS_MODULE=config.settings.production python manage.py migrate
DJANGO_SETTINGS_MODULE=config.settings.production python manage.py import_foods
```

## Standar Gizi yang Digunakan

| Standar | Referensi |
|---|---|
| AKG (Angka Kecukupan Gizi) | Permenkes No.28 Tahun 2019 |
| Kategori IMT | DEPKES RI (bukan WHO) |
| Data pangan | DKBM Indonesia via Nutrisurvey (937 bahan pangan) |
| Formula kalori basal | Mifflin-St Jeor |

### Distribusi Makronutrien (% energi)

| Makronutrien | % Energi | Formula |
|---|---|---|
| Protein | 13% | `(TDEE × 0.13) / 4` gram |
| Lemak | 25% | `(TDEE × 0.25) / 9` gram |
| Karbohidrat | 57.5% | `(TDEE × 0.575) / 4` gram |
| Serat | — | 25–30 g/hari (berdasarkan usia & jenis kelamin) |

### Kategori IMT (DEPKES RI)

| Nilai IMT | Kategori |
|---|---|
| < 17,0 | Kurus Berat |
| 17,0 – 18,5 | Kurus Ringan |
| 18,5 – 25,0 | Normal |
| 25,0 – 27,0 | Overweight |
| > 27,0 | Obesitas |

## Variabel Environment

| Variabel | Wajib | Deskripsi |
|---|---|---|
| `SECRET_KEY` | Ya | Django secret key |
| `DEBUG` | Ya | `True` untuk development, `False` untuk production |
| `DJANGO_SETTINGS_MODULE` | Ya | `config.settings.development` atau `config.settings.production` |
| `DB_NAME` | Production | Nama database PostgreSQL |
| `DB_USER` | Production | Username database |
| `DB_PASSWORD` | Production | Password database |
| `DB_HOST` | Production | Host database (Supabase pooler) |
| `DB_PORT` | Production | Port database (default: 5432) |

## Lisensi

Proyek ini dibuat untuk keperluan akademis.

Data pangan bersumber dari DKBM (Daftar Komposisi Bahan Makanan) Indonesia yang didistribusikan via Nutrisurvey.
