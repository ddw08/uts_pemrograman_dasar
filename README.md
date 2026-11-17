# Student Data Analyzer

Aplikasi **command line** untuk mengolah data mahasiswa: validasi, daftar bernomor, pencarian NIM,
filter, ranking, rekap statistik, serta impor/ekspor CSV dan penyimpanan JSON.

## Masalah, pengguna, input, dan output

| Item | Keterangan |
|------|------------|
| Masalah | Dosen/admin prodi menerima rekap nilai dan kehadiran dari berkas CSV yang sering salah ketik (nilai 101, nama kosong, NIM ganda). Dibutuhkan alat yang memeriksa data, menentukan status, dan membuat laporan. |
| Target pengguna | Dosen pengampu atau admin program studi. |
| Input | CSV (`nim,name,program,score,attendance`) atau isian lewat menu. |
| Output | Tampilan terminal, `data/mahasiswa.json` (penyimpanan), `output/laporan_mahasiswa.csv`, `output/laporan_ranking.csv`. |

## Fitur utama
1. **Impor CSV** dengan validasi per baris (baris salah dilewati dan dilaporkan alasannya).
2. **Tambah mahasiswa** dengan validasi dan penolakan NIM duplikat; input salah diminta ulang.
3. **Daftar bernomor + status otomatis**, **cari NIM**, dan **filter** berdasarkan status/prodi.
4. **Ranking** (nilai sama = rank sama) tanpa mengubah data asli.
5. **Rekap & statistik**: jumlah, rata-rata, min, maks, jumlah lulus, rekap per prodi, distribusi status.
6. **Ekspor laporan CSV** dan **penyimpanan JSON otomatis**.

## Cara menjalankan

Prasyarat: Python 3.10+ (tidak perlu instal library apa pun).

# virtual environment.
python -m venv .venv
source .venv/bin/activate        # macOS/Linux
.venv\Scripts\activate           # Windows

python main.py                   # jalankan aplikasi

Alur cepat: pilih **7** (impor `data/mahasiswa_input.csv`), lalu coba menu **1, 3, 4, 5, 6, 8**.


Melihat log DEBUG:

LOG_LEVEL=DEBUG python main.py            # macOS/Linux
$env:LOG_LEVEL="DEBUG"; python main.py    # Windows PowerShell

## Struktur project

UTS_Pemrograman_dasar/
├── main.py                  # menu & interaksi pengguna
├── analyzer/                # PACKAGE buatan sendiri
│   ├── __init__.py          # pintu masuk package 
│   ├── exceptions.py        # exception khusus
│   ├── validators.py        # aturan validasi data
│   ├── processing.py        # status, cari, filter, rekap, ranking
│   └── storage.py           # baca/tulis JSON & CSV
├── data/
│   ├── mahasiswa_input.csv  # contoh input
│   └── mahasiswa.json       # dibuat otomatis saat program dijalankan
├── debugging/               # skenario debugging Soal 6 + hasilnya
├── demo_input.txt           # skrip input untuk demo otomatis
├── requirements.txt
└── README.md

Alur dependensi antar-module:
`exceptions` ← `validators` ← `storage`; `exceptions` ← `processing`;
`main.py` memanggil `analyzer` (yang meneruskan ke keempat module itu).
`processing.py` tidak pernah menyentuh file, `storage.py` tidak pernah menghitung status.

## Aturan data
- NIM, nama, prodi: teks tidak kosong (spasi tepi dihapus). NIM hanya angka dan unik.
- Nilai & kehadiran: bilangan bulat 0–100. **0 sah**; `None`, teks kosong, `True`, `85.5`, `-1`, `101` ditolak.

Prioritas status (urutan penting):

| Urutan | Syarat | Status |
|--------|--------|--------|
| 1 | kehadiran < 75 | Peringatan Kehadiran |
| 2 | nilai ≥ 90 dan kehadiran ≥ 90 | Lulus dengan Pujian |
| 3 | nilai ≥ 80 | Lulus |
| 4 | nilai ≥ 60 | Remedial |
| 5 | selain itu | Tidak Lulus |

## Penanganan error 
| Kondisi | Perilaku |
|---------|----------|
| `mahasiswa.json` belum ada | mulai dengan data kosong (INFO) |
| JSON rusak / bukan list / ada record tidak valid | file disalin ke `*.rusak` (tidak dihapus), program tetap jalan (ERROR/WARNING) |
| File CSV tidak ditemukan | pesan jelas, kembali ke menu (WARNING) |
| Header CSV tidak lengkap | impor dibatalkan dengan pesan kolom yang kurang (ERROR) |
| Baris CSV tidak valid | dilewati, alasan ditampilkan |
| Input menu/isian salah | diminta ulang, data valid tidak hilang (WARNING) |
| Data kosong pada rekap/ranking/ekspor | pesan "Belum ada data." tanpa pembagian nol |
| Ctrl+C / akhir input | program keluar rapi |

## Package dan dependency
- Package buatan sendiri: `analyzer`.
- Library pihak ketiga: **tidak ada** (`requirements.txt` hanya berisi catatan).
- Standard library yang dipakai: `csv`, `json`, `logging`, `pathlib`, `shutil`, `datetime`, `operator`, `os`, `unittest`, `tempfile`.

## Referensi dan bantuan AI
- Modul Praktikum 1, 2, 3, 5, 6, 7.
- Dokumentasi Python: https://docs.python.org/3/
- PEP 8: https://peps.python.org/pep-0008/
-W3SCHOOLS: https://www.w3schools.com/python/default.asp
- **Bantuan AI:** kami meminta bantuan Claude, untuk membuat kerangka kode, lalu mengujinya, dan memcobanya sendiri. 
  Seluruh kode sudah dijalankan dan diuji, kemudian dipelajari.
