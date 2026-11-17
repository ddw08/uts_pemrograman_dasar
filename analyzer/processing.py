import logging
from operator import itemgetter

logger = logging.getLogger("analyzer.processing")

DAFTAR_STATUS = (
    "Lulus dengan Pujian",
    "Lulus",
    "Remedial",
    "Tidak Lulus",
    "Peringatan Kehadiran",
)
STATUS_LULUS = {"Lulus", "Lulus dengan Pujian"}
def tentukan_status(score, attendance):
    if attendance < 75:
        return "Peringatan Kehadiran"
    if score >= 90 and attendance >= 90:
        return "Lulus dengan Pujian"
    if score >= 80:
        return "Lulus"
    if score >= 60:
        return "Remedial"
    return "Tidak Lulus"

def tambah_status(students):
    return [
        {**s, "status": tentukan_status(s["score"], s["attendance"])}
        for s in students
    ]

def bangun_indeks_nim(students):
    return {s["nim"]: s for s in students}

def cari_nim(students, nim):
    return bangun_indeks_nim(students).get(nim.strip())

def prodi_unik(students):
    return {s["program"] for s in students}

def filter_status(students, status):
    return [s for s in tambah_status(students) if s["status"] == status]

def filter_prodi(students, prodi):
    """Pilih mahasiswa pada program studi tertentu (tidak peka huruf besar/kecil)."""
    target = prodi.strip().casefold()
    return [s for s in students if s["program"].casefold() == target]

def distribusi_status(students):
    """Hitung jumlah mahasiswa per status, termasuk status yang jumlahnya 0."""
    dengan_status = tambah_status(students)
    return {
        status: sum(1 for s in dengan_status if s["status"] == status)
        for status in DAFTAR_STATUS
    }

def hitung_ringkasan(students):
    if not students:
        logger.warning("Ringkasan diminta saat data kosong")
        return None
    nilai = [s["score"] for s in students]
    total = sum(nilai)
    logger.debug("Jumlah data = %d, total nilai = %d", len(nilai), total)
    return {
        "jumlah": len(students),
        "rata_rata": total / len(students),
        "minimum": min(nilai),
        "maksimum": max(nilai),
        "lulus": sum(
            1
            for s in students
            if tentukan_status(s["score"], s["attendance"]) in STATUS_LULUS
        ),
    }

def rekap_per_prodi(students):
    kelompok = {}
    for s in students:
        kelompok.setdefault(s["program"], []).append(s["score"])
    return {
        prodi: {"jumlah": len(nilai), "rata_rata": sum(nilai) / len(nilai)}
        for prodi, nilai in sorted(kelompok.items())
    }

def buat_ranking(students):
    urut = sorted(students, key=itemgetter("score"), reverse=True)
    hasil = []
    rank_sekarang = 0
    nilai_sebelumnya = None
    for posisi, s in enumerate(urut, start=1):
        if s["score"] != nilai_sebelumnya:
            rank_sekarang = posisi
            nilai_sebelumnya = s["score"]
        hasil.append({"rank": rank_sekarang, **s})
    return hasil