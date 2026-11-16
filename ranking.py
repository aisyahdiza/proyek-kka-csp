"""ranking.py - "AI" pemilih jadwal terbaik (dipegang Orang 3).

Solver CSP menghasilkan banyak jadwal VALID. Modul ini menilai tiap jadwal memakai
soft constraint (preferensi), lalu mengurutkannya. Tiap komponen bernilai 0..1 (makin besar makin baik).

Bobot bisa diubah di WEIGHTS. Bagian explain() bisa diganti/ditambah LLM kalau waktunya cukup.
"""
from typing import NamedTuple

WEIGHTS = {
    "preferensi_dosen": 0.30,   # kelas jatuh di slot favorit dosen
    "jeda_dosen": 0.25,         # jeda kosong antar kelas dosen di hari yang sama sedikit
    "sebaran_hari": 0.15,       # kelas tersebar ke banyak hari
    "hindari_sore": 0.15,       # tidak ada kelas mulai >= jam 16
    "kecocokan_ruang": 0.15,    # ruang tidak terlalu besar dibanding jumlah mahasiswa
}


class Ranked(NamedTuple):
    score: float        # 0..100
    schedule: dict
    breakdown: dict     # nama komponen -> nilai 0..1


def _slot_order(problem):
    """Per hari: daftar id slot terurut jam, untuk menghitung jeda."""
    by_day = {}
    for s in problem.slots.values():
        by_day.setdefault(s.day, []).append(s)
    return {d: [s.id for s in sorted(v, key=lambda x: x.start)] for d, v in by_day.items()}


def breakdown(schedule, problem):
    n = len(schedule)
    order = _slot_order(problem)

    # 1. preferensi dosen
    hits = sum(1 for a in schedule.values()
               if a.slot_id in problem.lecturers[a.lecturer_id].preferred_slots)
    preferensi = hits / n

    # 2. jeda dosen: (rentang kelas pertama-terakhir di sebuah hari) - (jumlah kelas), dijumlah semua dosen
    gaps = 0
    per_lecturer_day = {}
    for a in schedule.values():
        day = problem.slots[a.slot_id].day
        per_lecturer_day.setdefault((a.lecturer_id, day), []).append(order[day].index(a.slot_id))
    for idxs in per_lecturer_day.values():
        gaps += (max(idxs) - min(idxs) + 1) - len(idxs)
    jeda = max(0.0, 1 - gaps / n)

    # 3. sebaran hari
    days_used = len({problem.slots[a.slot_id].day for a in schedule.values()})
    days_total = len({s.day for s in problem.slots.values()})
    sebaran = days_used / min(n, days_total)

    # 4. hindari sore
    late = sum(1 for a in schedule.values() if problem.slots[a.slot_id].start >= 16)
    sore = 1 - late / n

    # 5. kecocokan ruang
    fit = sum(problem.sections[sid].size / problem.rooms[a.room_id].capacity
              for sid, a in schedule.items()) / n

    return {
        "preferensi_dosen": preferensi,
        "jeda_dosen": jeda,
        "sebaran_hari": sebaran,
        "hindari_sore": sore,
        "kecocokan_ruang": fit,
    }


def score(schedule, problem):
    bd = breakdown(schedule, problem)
    return 100 * sum(WEIGHTS[k] * v for k, v in bd.items()), bd


def rank(schedules, problem, top_k=5):
    """Urutkan jadwal valid dari skor tertinggi. Mengembalikan list Ranked (maks top_k)."""
    ranked = []
    for sch in schedules:
        s, bd = score(sch, problem)
        ranked.append(Ranked(round(s, 2), sch, bd))
    ranked.sort(key=lambda r: r.score, reverse=True)
    return ranked[:top_k]


def explain(ranked, problem):
    """Penjelasan singkat kenapa jadwal ini direkomendasikan (berbasis aturan).
    BONUS: kirim `ranked.breakdown` ke LLM untuk penjelasan yang lebih natural."""
    labels = {
        "preferensi_dosen": "banyak kelas jatuh di jam favorit dosen",
        "jeda_dosen": "jeda kosong dosen sedikit",
        "sebaran_hari": "kelas tersebar ke beberapa hari",
        "hindari_sore": "tidak ada kelas sore",
        "kecocokan_ruang": "ukuran ruang pas dengan jumlah mahasiswa",
    }
    top = sorted(ranked.breakdown.items(), key=lambda kv: kv[1], reverse=True)[:2]
    weak = min(ranked.breakdown.items(), key=lambda kv: kv[1])
    return (f"Skor {ranked.score}/100. Kelebihan: {labels[top[0][0]]} dan {labels[top[1][0]]}. "
            f"Titik terlemah: {weak[0].replace('_', ' ')} (nilai {weak[1]:.0%}).")
