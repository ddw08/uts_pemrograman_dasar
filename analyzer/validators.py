from .exceptions import DataMahasiswaError, NamaKosongError, NimDuplikatError

KOLOM_WAJIB = ("nim", "name", "program", "score", "attendance")


def validasi_teks(value, label):
    if not isinstance(value, str) or not value.strip():
        raise DataMahasiswaError(f"{label} wajib diisi.")
    return value.strip()


def validasi_nim(value, nim_terpakai=frozenset()):
    nim = validasi_teks(value, "NIM")
    if not nim.isdigit():
        raise DataMahasiswaError("NIM harus berupa angka.")
    if nim in nim_terpakai:
        raise NimDuplikatError(f"NIM {nim} sudah terdaftar.")
    return nim


def validasi_nama(value):
    if not isinstance(value, str) or not value.strip():
        raise NamaKosongError("Nama wajib diisi.")
    return value.strip()


def validasi_prodi(value):
    return validasi_teks(value, "Program studi")


def ubah_ke_int(teks, label):
    if not isinstance(teks, str) or not teks.strip():
        raise DataMahasiswaError(f"{label} wajib diisi.")
    try:
        return int(teks.strip())
    except ValueError as error:
        raise DataMahasiswaError(f"{label} harus bilangan bulat.") from error


def validasi_angka_0_100(value, label):
    if type(value) is not int:
        raise DataMahasiswaError(f"{label} harus bilangan bulat.")
    if not 0 <= value <= 100:
        raise DataMahasiswaError(f"{label} harus antara 0 dan 100.")
    return value


def _angka(value, label):
    if value is None:
        raise DataMahasiswaError(f"{label} wajib diisi.")
    if isinstance(value, str):
        value = ubah_ke_int(value, label)
    return validasi_angka_0_100(value, label)


def baca_nilai(value):
    return _angka(value, "Nilai")


def baca_kehadiran(value):
    return _angka(value, "Kehadiran")


def validasi_mahasiswa(record, nim_terpakai=frozenset()):
    if not isinstance(record, dict):
        raise DataMahasiswaError("Record harus berupa dictionary/objek.")
    return {
        "nim": validasi_nim(record.get("nim"), nim_terpakai),
        "name": validasi_nama(record.get("name")),
        "program": validasi_prodi(record.get("program")),
        "score": baca_nilai(record.get("score")),
        "attendance": baca_kehadiran(record.get("attendance")),
    }
