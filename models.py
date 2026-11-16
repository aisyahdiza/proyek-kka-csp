"""models.py - struktur data inti (dipegang Orang 1).

Jangan ubah nama/bentuk class ini tanpa kabar ke ketua, karena semua modul memakainya.
"""
from dataclasses import dataclass
from typing import NamedTuple


class Assignment(NamedTuple):
    """Nilai domain CSP: satu kelas diajar dosen X, di ruang Y, pada slot Z."""
    lecturer_id: str
    room_id: str
    slot_id: str


@dataclass(frozen=True)
class Lecturer:
    id: str
    name: str
    available_slots: frozenset   # slot_id yang bisa diajar dosen ini
    preferred_slots: frozenset   # slot_id favorit (dipakai soft constraint)
    max_load: int                # maksimal jumlah kelas yang diajar


@dataclass(frozen=True)
class Room:
    id: str
    name: str
    capacity: int


@dataclass(frozen=True)
class Slot:
    id: str       # contoh "Sen-08"
    day: str      # "Sen", "Sel", "Rab", "Kam", "Jum"
    start: int    # jam mulai, contoh 8
    end: int      # jam selesai, contoh 10


@dataclass(frozen=True)
class Section:
    """Variabel CSP: satu kelas yang harus dijadwalkan."""
    id: str
    course: str
    sks: int
    size: int                    # jumlah mahasiswa / kuota kelas
    eligible_lecturers: tuple    # id dosen yang boleh mengajar kelas ini
    group: str = ""              # kelompok mahasiswa (misal angkatan/kelas wajib); "" = tidak dikelompokkan
    course_code: str = ""        # kode mata kuliah; beberapa section bisa satu kode (dipakai krs.py); "" = pakai nama


@dataclass
class Problem:
    lecturers: dict   # id -> Lecturer
    rooms: dict       # id -> Room
    slots: dict       # id -> Slot
    sections: dict    # id -> Section


# Schedule = dict {section_id: Assignment}
