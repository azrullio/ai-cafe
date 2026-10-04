# AI Cafe Surabaya

Asisten pencari tempat nongkrong di **Surabaya, Kota Seribu Warkop**. Cari cafe, warkop, **STK (Sedulur Tunggal Kopi)**, kedai, dan resto dengan bahasa sehari-hari, lalu saring berdasarkan rating, jam buka, wilayah, jarak, dan fasilitas. Setiap tempat punya tombol **Buka Google Maps** dan **Rute ke sini**.

Data bawaan: **896 tempat** (513 resto, 231 cafe, 130 warkop, 18 kedai, 4 STK) dari OpenStreetMap ditambah daftar kurasi dari artikel kuliner.

---

## Daftar isi

1. [Isi repo](#isi-repo)
2. [Cara menjalankan](#cara-menjalankan)
3. [Cara menggunakan aplikasi](#cara-menggunakan-aplikasi)
4. [Mendapatkan Google Places API key](#mendapatkan-google-places-api-key)
5. [Mengambil data lengkap dengan API](#mengambil-data-lengkap-dengan-api)
6. [Memperbarui data bawaan (OpenStreetMap)](#memperbarui-data-bawaan-openstreetmap)
7. [Format data](#format-data)
8. [Keterbatasan data](#keterbatasan-data)
9. [Sumber dan lisensi data](#sumber-dan-lisensi-data)

---

## Isi repo

| File | Fungsi |
|---|---|
| `ai-cafe.html` | Aplikasinya. Satu file HTML, data bawaan sudah ada di dalamnya. |
| `ai-cafe-data.json` | Data bawaan dalam bentuk JSON (sama dengan yang ada di HTML). |
| `fetch_places.py` | Mengambil data lengkap dari **Google Places API** (rating, jam buka, telepon, dll.) → `ai-cafe-data.json`. |
| `build_data.py` | Menggabungkan data OpenStreetMap + daftar kurasi → `ai-cafe-data.json`, lalu menyisipkannya ke `ai-cafe.html`. |
| `data/osm.json`, `data/osm2.json` | Data mentah OpenStreetMap. |
| `data/overpass_*.ql` | Query Overpass untuk mengunduh ulang data OpenStreetMap. |

## Cara menjalankan

Aplikasi ini tidak butuh instalasi atau server khusus.

**Cara 1: buka langsung.** Klik dua kali `ai-cafe.html`, nanti terbuka di browser.

**Cara 2: lewat server lokal** (disarankan, supaya perilakunya sama seperti di hosting):

```bash
python -m http.server 8000
```

Lalu buka `http://localhost:8000/ai-cafe.html` di browser.

**Cara 3: online lewat GitHub Pages.**
1. Di repo GitHub, buka **Settings → Pages**.
2. Pada **Source**, pilih **Deploy from a branch**, branch `main`, folder `/ (root)`, lalu **Save**.
3. Setelah 1–2 menit, aplikasi bisa dibuka di `https://<username>.github.io/<nama-repo>/ai-cafe.html`.

> GitHub Pages hanya tersedia untuk repo publik, kecuali akunmu GitHub Pro.

## Cara menggunakan aplikasi

### Tanya ke Asisten AI Cafe
Ketik kebutuhanmu di kotak asisten, misalnya:

- `warkop 24 jam dekat ITS`
- `STK buka sekarang`
- `cafe buat kerja ada wifi colokan`
- `nongkrong jam 1 malam di Surabaya Timur`
- `cafe rating 4.5 di Tunjungan`
- `tempat makan legendaris`

Asisten mengenali:

| Yang dikenali | Contoh kata |
|---|---|
| Jenis tempat | cafe, kopi, warkop, cangkruk, STK, sedulur tunggal, kedai, resto, makan, depot |
| Rating | `rating 4.5`, `bintang 4`, `terbaik`, `rekomen` |
| Waktu | `buka sekarang`, `24 jam`, `jam 10 malam`, `jam 2 malam`, `pagi`, `sore`, `besok`, nama hari |
| Wilayah | pusat, utara, timur, selatan, barat, Sukolilo, Rungkut, Wonokromo, Citraland, dll. |
| Titik acuan | ITS, Unair, Tunjungan Plaza, Tugu Pahlawan, Stasiun Gubeng, Taman Bungkul, Galaxy Mall, Royal Plaza, Pakuwon Mall, Kenjeran (+ `3 km` untuk radius) |
| Fasilitas | wifi, colokan, kerja/nugas, outdoor, rokok, parkir, murah, estetik, legendaris, rombongan, date |

Filter di panel kiri otomatis menyesuaikan, dan asisten menampilkan 3 rekomendasi teratas. Kalau tidak ada hasil, asisten melonggarkan syarat (misalnya fasilitas atau jam yang belum tercatat) dan memberi tahu syarat mana yang dilepas.

> Asisten ini bekerja dengan pencocokan kata kunci di browser, tanpa model AI online, jadi bisa dipakai gratis dan offline.

### Filter manual
- **Jenis tempat**: Cafe, Warkop, Kedai, Resto, STK.
- **Rating minimum**: Semua, 4.0+, 4.3+, 4.5+. Tempat tanpa rating ikut tersaring keluar.
- **Jam buka**: Kapan saja, Buka sekarang, atau Pilih jam (hari + jam).
- **Wilayah**: Pusat, Utara, Timur, Selatan, Barat.
- **Dekat dengan**: pilih titik acuan lalu geser radius (1–15 km). Urutan otomatis menjadi "Terdekat".
- **Fasilitas & suasana**, **Harga**, dan **Urutkan** (rating, ulasan, terdekat, nama).

### Detail tempat dan Google Maps
Klik kartu atau titik di peta untuk membuka detail: alamat, koordinat (bisa disalin), jam buka per hari, fasilitas, telepon, website, dan sumber data. Tombol:
- **Buka Google Maps** membuka pencarian tempat itu di Google Maps.
- **Rute ke sini** membuka petunjuk arah Google Maps ke koordinatnya.

### Impor data
Tombol **Impor data** (kanan atas) memuat file JSON, misalnya hasil `fetch_places.py`. Data impor tersimpan di browser, dan bisa dikembalikan ke data bawaan lewat tautan **Kembali ke data bawaan** di bagian bawah halaman.

## Mendapatkan Google Places API key

Data bawaan belum lengkap untuk rating dan jam buka. Data lengkap diambil dari Google Places API.

1. Buka **https://console.cloud.google.com/** dan login dengan akun Google.
2. Buat project baru: klik pemilih project di atas → **New Project** → beri nama (misalnya `ai-cafe`) → **Create**.
3. Aktifkan billing: menu **Billing** → hubungkan akun penagihan (kartu kredit/debit). Google mewajibkan ini untuk Places API, dan ada kuota gratis bulanan. Cek angka terbarunya di https://mapsplatform.google.com/pricing/.
4. Aktifkan API: menu **APIs & Services → Library**, cari **Places API (New)**, lalu **Enable**.
5. Buat key: **APIs & Services → Credentials → Create credentials → API key**. Salin key-nya.
6. Batasi key (penting): klik key tersebut → **API restrictions → Restrict key** → centang **Places API (New)** → **Save**.
7. (Disarankan) Pasang batas pemakaian di **APIs & Services → Places API (New) → Quotas** dan **Billing → Budgets & alerts**, supaya tagihan tidak membengkak.

> **Jangan pernah commit API key ke GitHub.** Simpan di environment variable seperti contoh di bawah. File `.env` sudah dimasukkan ke `.gitignore`.

## Mengambil data lengkap dengan API

Butuh Python 3.9+.

```bash
pip install requests
```

**Windows PowerShell:**

```powershell
$env:GOOGLE_MAPS_API_KEY="KEY_KAMU"
python fetch_places.py
```

**macOS / Linux / Git Bash:**

```bash
GOOGLE_MAPS_API_KEY=KEY_KAMU python fetch_places.py
```

Yang dilakukan script:
- Membagi Surabaya menjadi grid 5×6 (30 area) dan mencari `cafe`, `coffee shop`, `warkop`, `warung kopi`, `kedai`, `Sedulur Tunggal Kopi`, `warkop STK`, `restoran`, dan `rumah makan` di setiap area (maks. 60 hasil per pencarian).
- Mengambil nama, alamat, koordinat, rating, jumlah ulasan, harga, jam buka, telepon, website, link Google Maps, dan fasilitas (outdoor, live music, parkir, dll.).
- Menghapus duplikat dan tempat yang sudah tutup permanen.
- Menyimpan hasilnya ke `ai-cafe-data.json`.

Setelah selesai, buka aplikasi → **Impor data** → pilih `ai-cafe-data.json`.

**Mengatur biaya:** jumlah permintaan kira-kira `sel grid × jumlah kata kunci × halaman` (maks. 30 × 9 × 3 = 810). Untuk berhemat:
- Kecilkan `GRID_ROWS` / `GRID_COLS` di `fetch_places.py`.
- Kurangi daftar `QUERIES`.
- Hapus field atmosfer (`outdoorSeating`, `liveMusic`, dll.) dari `FIELD_MASK`, karena field itu masuk tarif yang lebih mahal.

**Ketentuan Google:** konten Places (selain `place_id`) tidak boleh disimpan permanen. Jalankan ulang script secara berkala (misalnya sebulan sekali), dan jangan commit hasil Google ke repo publik.

## Memperbarui data bawaan (OpenStreetMap)

Data OpenStreetMap gratis dan tidak butuh API key.

```bash
curl -A "AICafe/1.0" --data-urlencode "data@data/overpass_food.ql" https://overpass-api.de/api/interpreter -o data/osm.json
```

```bash
curl -A "AICafe/1.0" --data-urlencode "data@data/overpass_names.ql" https://overpass-api.de/api/interpreter -o data/osm2.json
```

```bash
python build_data.py
```

`build_data.py` menggabungkan data OSM dengan daftar kurasi (`CURATED` di dalam script), mencari koordinat tempat kurasi lewat Nominatim, lalu menulis `ai-cafe-data.json` dan menyisipkannya ke `ai-cafe.html`.

**Menambah tempat favoritmu:** tambahkan baris baru di `CURATED` dalam `build_data.py`, misalnya:

```python
dict(name="Warkop Contoh", category="warkop", address="Jl. Contoh No.1, Gubeng",
     hours="24/7", tags=["wifi", "colokan", "murah"]),
```

Lalu jalankan `python build_data.py` lagi. Kalau alamatnya tidak ketemu, tambahkan `ll=(lat, lng)` untuk koordinat manual.

## Format data

`ai-cafe-data.json` berisi array objek. Field yang dikenali aplikasi:

| Field | Wajib | Keterangan |
|---|---|---|
| `name` | ya | Nama tempat |
| `lat`, `lng` | ya | Koordinat (angka) |
| `category` | | `cafe`, `warkop`, `kedai`, `resto`, atau `stk` |
| `address` | | Alamat |
| `rating`, `reviews` | | Rating (0–5) dan jumlah ulasan |
| `periods` | | Jam buka: `[[mulai, selesai], ...]` dalam menit sejak Minggu 00:00 (0–10080). `[[0,10080]]` = 24 jam. |
| `open`, `close` | | Alternatif `periods` yang lebih sederhana, misalnya `"08:00"`, `"22:00"` (berlaku setiap hari) |
| `price` | | 1 (murah) – 4 (mahal) |
| `tags` | | Daftar fasilitas, misalnya `["wifi","outdoor"]` |
| `phone`, `website`, `mapsUrl`, `placeId` | | Opsional |

## Keterbatasan data

- **Rating:** baru 24 tempat di data bawaan yang punya rating (dari artikel atau perkiraan AI, dan yang perkiraan diberi label). OpenStreetMap tidak menyimpan rating.
- **Jam buka:** baru tercatat di 325 tempat. Tempat tanpa jam tidak muncul saat filter jam dipakai.
- **STK:** baru 4 cabang yang terpetakan di OpenStreetMap. Gunakan `fetch_places.py` untuk daftar cabang lengkap.
- **Lokasi:** beberapa tempat kurasi hanya punya titik perkiraan tingkat jalan atau kawasan (ditandai di detail tempat).
- **Peta di aplikasi** berupa peta skematik, bukan peta navigasi. Untuk navigasi gunakan tombol Google Maps.

Selalu cek Google Maps untuk info terbaru sebelum berangkat.

## Sumber dan lisensi data

- Data tempat: © kontributor [OpenStreetMap](https://www.openstreetmap.org/copyright), lisensi ODbL.
- Daftar kurasi dan rating dari artikel: JawaPos, detik.com, IDN Times, dan Mojok (sumber per tempat tercantum di field `src`).
- Data dari Google Places API tunduk pada [ketentuan Google Maps Platform](https://cloud.google.com/maps-platform/terms).
