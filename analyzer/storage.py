import csv
import json
import logging
import shutil
from datetime import datetime
from pathlib import Path

from .exceptions import DataMahasiswaError, FormatFileError
from .validators import KOLOM_WAJIB, validasi_mahasiswa

logger = logging.getLogger("analyzer.storage")


def validasi_banyak(rows, nim_terpakai=None):
    nim_terpakai = set(nim_terpakai or ())
    valid = []
    ditolak = []
    for nomor, row in enumerate(rows, start=1):
        try:
            record = validasi_mahasiswa(row, nim_terpakai)
        except DataMahasiswaError as error:
            logger.warning("Baris data %d ditolak: %s", nomor, error)
            ditolak.append((nomor, str(error)))
        else:
            nim_terpakai.add(record["nim"])
            valid.append(record)
    return valid, ditolak


def _cadangkan(path):
    stempel = datetime.now().strftime("%Y%m%d_%H%M%S")
    cadangan = path.with_name(f"{path.name}.{stempel}.rusak")
    shutil.copy2(path, cadangan)
    return cadangan


def muat_json(path):
    path = Path(path)
    try:
        with open(path, "r", encoding="utf-8") as file:
            mentah = json.load(file)
    except FileNotFoundError:
        logger.info("File %s belum ada, mulai dengan data kosong", path.name)
        return []
    except (json.JSONDecodeError, UnicodeDecodeError) as error:
        cadangan = _cadangkan(path)
        logger.error(
            "%s rusak (%s: %s). Salinan disimpan di %s",
            path.name, type(error).__name__, error, cadangan.name,
        )
        return []

    if not isinstance(mentah, list):
        cadangan = _cadangkan(path)
        logger.error(
            "%s harus berisi list, bukan %s. Salinan disimpan di %s",
            path.name, type(mentah).__name__, cadangan.name,
        )
        return []

    valid, ditolak = validasi_banyak(mentah)
    if ditolak:
        cadangan = _cadangkan(path)
        logger.warning(
            "%d record di %s tidak valid dan dilewati. Salinan asli: %s",
            len(ditolak), path.name, cadangan.name,
        )
    logger.info("%d record dimuat dari %s", len(valid), path.name)
    return valid


def simpan_json(students, path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    sementara = path.with_name(path.name + ".tmp")
    with open(sementara, "w", encoding="utf-8") as file:
        json.dump(students, file, indent=2, ensure_ascii=False)
    sementara.replace(path)
    logger.info("%d record disimpan ke %s", len(students), path.name)


def baca_csv(path):
    path = Path(path)
    try:
        with open(path, "r", newline="", encoding="utf-8-sig") as file:
            reader = csv.DictReader(file)
            kolom_ada = set(reader.fieldnames or [])
            kolom_hilang = [k for k in KOLOM_WAJIB if k not in kolom_ada]
            if kolom_hilang:
                raise FormatFileError(
                    f"Kolom CSV tidak lengkap, kurang: {', '.join(kolom_hilang)}"
                )
            return list(reader)
    except (csv.Error, UnicodeDecodeError) as error:
        raise FormatFileError(f"CSV tidak dapat dibaca: {error}") from error


def ekspor_csv(rows, path, fieldnames):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    logger.info("Laporan CSV dibuat: %s (%d baris)", path.name, len(rows))
    return len(rows)
