class DataMahasiswaError(ValueError):
    """Dasar semua kesalahan isian data mahasiswa."""


class NamaKosongError(DataMahasiswaError):
    """Nama mahasiswa tidak boleh kosong."""


class NimDuplikatError(DataMahasiswaError):
    """NIM sudah dipakai mahasiswa lain."""


class FormatFileError(ValueError):
    """Isi/struktur file tidak sesuai format yang diharapkan."""
