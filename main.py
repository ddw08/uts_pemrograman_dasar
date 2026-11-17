import logging
import os
from pathlib import Path

from analyzer import (
    DAFTAR_STATUS,
    DataMahasiswaError,
    FormatFileError,
    baca_csv,
    baca_kehadiran,
    baca_nilai,
    buat_ranking,
    cari_nim,
    distribusi_status,
    ekspor_csv,
    filter_prodi,
    filter_status,
    hitung_ringkasan,
    muat_json,
    prodi_unik,
    rekap_per_prodi,
    simpan_json,
    tambah_status,
    validasi_banyak,
    validasi_nama,
    validasi_nim,
    validasi_prodi,
)

BASE_DIR = Path(__file__).resolve().parent
DATA_JSON = BASE_DIR / "data" / "mahasiswa.json"
CSV_INPUT = BASE_DIR / "data" / "mahasiswa_input.csv"
OUTPUT_DIR = BASE_DIR / "output"

LEVEL = getattr(logging, os.environ.get("LOG_LEVEL", "INFO").upper(), logging.INFO)
logging.basicConfig(level=LEVEL, format="%(levelname)s: %(message)s")
logger = logging.getLogger("main")

MENU = """
==============================================
            STUDENT DATA ANALYZER
==============================================
1. Tampilkan Semua Mahasiswa
2. Tambah Mahasiswa
3. Cari Mahasiswa (NIM)
4. Filter (Status / Program Studi)
5. Ranking Mahasiswa
6. Rekap & Statistik
7. Impor Data dari CSV
8. Ekspor Laporan ke CSV
9. Keluar
=============================================="""


def minta_input(prompt, validator):
    while True:
        try:
            hasil = validator(input(prompt))
        except ValueError as error:  
            logger.warning("Input ditolak: %s", error)
            print(f"Input salah: {error}")
        else:
            return hasil


def pilih_opsi(teks, opsi):
    teks = teks.strip()
    if not teks.isdigit() or not 1 <= int(teks) <= len(opsi):
        raise ValueError(f"Pilih angka 1 sampai {len(opsi)}.")
    return opsi[int(teks) - 1]


def tampilkan_daftar(students, judul=None):
    if judul:
        print(f"\n{judul}")
    if not students:
        print("Belum ada data.")
        return
    print(
        f"{'No':>3} | {'NIM':<8} | {'Nama':<14} | {'Prodi':<17} | "
        f"{'Nilai':>5} | {'Hadir':>5} | Status"
    )
    print("-" * 82)
    for nomor, s in enumerate(tambah_status(students), start=1):
        print(
            f"{nomor:>3} | {s['nim']:<8} | {s['name']:<14} | {s['program']:<17} | "
            f"{s['score']:>5} | {s['attendance']:>4}% | {s['status']}"
        )


def tampilkan_ranking(ranking):
    print("\nRANKING MAHASISWA")
    print("-" * 46)
    for s in ranking:
        print(f"Rank {s['rank']}: {s['name']:<14} - {s['score']:>3}  ({s['program']})")


def simpan_aman(students):
    try:
        simpan_json(students, DATA_JSON)
    except OSError as error:
        logger.error("Gagal menyimpan data (%s): %s", type(error).__name__, error)
        print("Data tidak dapat disimpan ke file. Periksa izin folder data/.")


def menu_tambah(students):
    nim_terpakai = {s["nim"] for s in students}
    nim = minta_input("NIM        : ", lambda t: validasi_nim(t, nim_terpakai))
    nama = minta_input("Nama       : ", validasi_nama)
    prodi = minta_input("Prodi      : ", validasi_prodi)
    nilai = minta_input("Nilai (0-100)     : ", baca_nilai)
    hadir = minta_input("Kehadiran % (0-100): ", baca_kehadiran)
    students.append(
        {"nim": nim, "name": nama, "program": prodi, "score": nilai, "attendance": hadir}
    )
    logger.info("Data mahasiswa berhasil ditambahkan")
    print("Data ditambahkan.")
    simpan_aman(students)


def menu_cari(students):
    if not students:
        print("Belum ada data.")
        return
    nim = input("Masukkan NIM: ").strip()
    ditemukan = cari_nim(students, nim)
    if ditemukan is None:
        print("Mahasiswa tidak ditemukan.")
        return
    tampilkan_daftar([ditemukan], judul="Hasil pencarian:")


def menu_filter(students):
    if not students:
        print("Belum ada data.")
        return
    print("1. Berdasarkan status\n2. Berdasarkan program studi")
    jenis = minta_input("Pilih filter: ", lambda t: pilih_opsi(t, ("status", "prodi")))
    if jenis == "status":
        for nomor, status in enumerate(DAFTAR_STATUS, start=1):
            print(f"{nomor}. {status}")
        status = minta_input("Pilih status: ", lambda t: pilih_opsi(t, DAFTAR_STATUS))
        tampilkan_daftar(filter_status(students, status), judul=f"Status: {status}")
    else:
        daftar_prodi = sorted(prodi_unik(students))
        for nomor, prodi in enumerate(daftar_prodi, start=1):
            print(f"{nomor}. {prodi}")
        prodi = minta_input("Pilih prodi: ", lambda t: pilih_opsi(t, daftar_prodi))
        tampilkan_daftar(filter_prodi(students, prodi), judul=f"Program studi: {prodi}")


def menu_ranking(students):
    if not students:
        print("Belum ada data.")
        return
    tampilkan_ranking(buat_ranking(students))
    logger.info("Laporan ranking berhasil dibuat")


def menu_rekap(students):
    ringkasan = hitung_ringkasan(students)
    if ringkasan is None:  
        print("Belum ada data.")
        return
    print("\nRINGKASAN")
    print(f"Jumlah mahasiswa : {ringkasan['jumlah']}")
    print(f"Rata-rata nilai  : {ringkasan['rata_rata']:.2f}")
    print(f"Nilai terendah   : {ringkasan['minimum']}")
    print(f"Nilai tertinggi  : {ringkasan['maksimum']}")
    print(f"Jumlah lulus     : {ringkasan['lulus']}")

    unik = sorted(prodi_unik(students))
    print(f"\nProgram studi unik ({len(unik)}): {', '.join(unik)}")
    print("\nREKAP PER PRODI")
    for prodi, data in rekap_per_prodi(students).items():
        print(f"- {prodi:<17}: {data['jumlah']} mahasiswa, rata-rata {data['rata_rata']:.2f}")

    print("\nDISTRIBUSI STATUS")
    for status, jumlah in distribusi_status(students).items():
        print(f"- {status:<20}: {jumlah}")
    logger.info("Laporan rekap berhasil dibuat")


def menu_impor(students):
    teks = input(f"Path file CSV [{CSV_INPUT.relative_to(BASE_DIR)}]: ").strip()
    path = Path(teks) if teks else CSV_INPUT
    try:
        rows = baca_csv(path)
    except FileNotFoundError:
        logger.warning("File CSV tidak ditemukan: %s", path)
        print(f"File tidak ditemukan: {path}")
        return
    except (FormatFileError, OSError) as error:
        logger.error("Impor gagal (%s): %s", type(error).__name__, error)
        print(f"Impor gagal: {error}")
        return

    valid, ditolak = validasi_banyak(rows, {s["nim"] for s in students})
    students.extend(valid)
    print(f"Impor selesai: {len(valid)} diterima, {len(ditolak)} ditolak.")
    for nomor, alasan in ditolak:
        print(f"  - baris data {nomor}: {alasan}")
    if valid:
        simpan_aman(students)


def menu_ekspor(students):
    if not students:
        logger.warning("Ekspor dibatalkan karena data kosong")
        print("Belum ada data untuk diekspor.")
        return
    try:
        ekspor_csv(
            tambah_status(students),
            OUTPUT_DIR / "laporan_mahasiswa.csv",
            ["nim", "name", "program", "score", "attendance", "status"],
        )
        ekspor_csv(
            buat_ranking(students),
            OUTPUT_DIR / "laporan_ranking.csv",
            ["rank", "nim", "name", "program", "score"],
        )
    except OSError as error:
        logger.error("Ekspor gagal (%s): %s", type(error).__name__, error)
        print("Ekspor gagal. Periksa izin folder output/.")
        return
    print("CSV dibuat di folder output/: laporan_mahasiswa.csv dan laporan_ranking.csv")


def main():
    logger.info("Program dimulai")
    try:
        students = muat_json(DATA_JSON)
    except OSError as error:
        logger.error("Gagal membaca %s (%s): %s", DATA_JSON.name, type(error).__name__, error)
        students = []

    aksi = {
        "1": lambda: tampilkan_daftar(students, judul="DAFTAR MAHASISWA"),
        "2": lambda: menu_tambah(students),
        "3": lambda: menu_cari(students),
        "4": lambda: menu_filter(students),
        "5": lambda: menu_ranking(students),
        "6": lambda: menu_rekap(students),
        "7": lambda: menu_impor(students),
        "8": lambda: menu_ekspor(students),
    }

    try:
        while True:
            print(MENU)
            pilihan = input("Pilihan: ").strip()
            logger.debug("Pilihan menu: %r", pilihan)
            if pilihan == "9":
                print("Selesai.")
                break
            if pilihan in aksi:
                aksi[pilihan]()
            else:
                logger.warning("Pilihan menu tidak tersedia: %r", pilihan)
                print("Pilihan tidak tersedia.")
    except (EOFError, KeyboardInterrupt):
        print("\nInput dihentikan.")
    finally:
        logger.info("Program selesai")


if __name__ == "__main__":
    main()
