import csv
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))  

from analyzer import FormatFileError, baca_csv  # noqa: E402


def status_salah(score, attendance):
    if score >= 90 and attendance >= 90:
        return "Lulus dengan Pujian"
    if score >= 80:
        return "Lulus" 
    if attendance < 75:
        return "Peringatan Kehadiran"
    if score >= 60:
        return "Remedial"
    return "Tidak Lulus"


def skenario_a():
    dewi = {"name": "Dewi", "score": 88, "attendance": 70}
    status = status_salah(dewi["score"], dewi["attendance"])
    print(f"{dewi['name']}: {status}")  



def baca_nama_naif(path):
    with open(path, "r", newline="", encoding="utf-8") as file:
        return [row["name"] for row in csv.DictReader(file)]


def skenario_b():
    print(baca_nama_naif(RAIZ / "debugging" / "header_salah.csv"))


def skenario_b_diperbaiki():
    try:
        baca_csv(RAIZ / "debugging" / "header_salah.csv")
    except FormatFileError as error:
        print(f"Impor gagal: {error}")


if __name__ == "__main__":
    pilihan = sys.argv[1] if len(sys.argv) > 1 else "a"
    {"a": skenario_a, "b": skenario_b, "b2": skenario_b_diperbaiki}[pilihan]()
