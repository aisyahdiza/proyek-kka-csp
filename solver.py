"""solver.py - solver CSP (dipegang Orang 1).

Satu fungsi inti, solve_with_stats, yang tekniknya bisa dinyalakan/dimatikan:
  - use_mrv : pilih kelas dengan domain tersisa PALING SEDIKIT (kalau mati: urutan tetap)
  - use_fc  : forward checking, buang nilai domain kelas lain yang pasti bentrok
              (kalau mati: konsistensi baru dicek saat sebuah nilai dicoba, "backtracking biasa")

Empat varian untuk dibandingkan (lihat compare.py):
  BT biasa | BT + MRV | BT + FC | BT + MRV + FC

Statistik yang dicatat tiap pencarian:
  nodes      = berapa kali fungsi rekursi dipanggil (ukuran pohon pencarian)
  backtracks = berapa kali sebuah penugasan dibatalkan
  checks     = berapa kali is_consistent dipanggil (biaya kerja sebenarnya)
  ms         = waktu eksekusi
"""
import random
import time

from constraints import build_domain, is_consistent


def solve_with_stats(problem, use_mrv=True, use_fc=True, rng=None, max_nodes=200000):
    """Cari SATU jadwal valid. Mengembalikan (solusi_atau_None, stats)."""
    rng = rng or random.Random()
    t0 = time.perf_counter()
    stats = {"nodes": 0, "backtracks": 0, "checks": 0, "ms": 0.0, "aborted": False}

    domains = {sid: build_domain(sec, problem) for sid, sec in problem.sections.items()}
    if any(not d for d in domains.values()):
        stats["ms"] = (time.perf_counter() - t0) * 1000
        return None, stats  # ada kelas yang tidak punya pilihan sama sekali
    for d in domains.values():
        rng.shuffle(d)

    partial = {}

    def backtrack(doms):
        # doms hanya berisi kelas yang BELUM dijadwalkan
        if not doms:
            return dict(partial)
        stats["nodes"] += 1
        if stats["nodes"] > max_nodes:
            stats["aborted"] = True
            return None

        sid = min(doms, key=lambda s: len(doms[s])) if use_mrv else next(iter(doms))

        for value in doms[sid]:
            if stats["aborted"]:
                return None
            if not use_fc:                      # BT biasa: cek konflik saat nilai dicoba
                stats["checks"] += 1
                if not is_consistent(sid, value, partial, problem):
                    continue
            partial[sid] = value

            rest = {k: v for k, v in doms.items() if k != sid}
            ok = True
            if use_fc:                          # FC: saring domain kelas lain
                filtered_rest = {}
                for other, d in rest.items():
                    kept = []
                    for v in d:
                        stats["checks"] += 1
                        if is_consistent(other, v, partial, problem):
                            kept.append(v)
                    if not kept:
                        ok = False
                        break
                    filtered_rest[other] = kept
                rest = filtered_rest

            if ok:
                result = backtrack(rest)
                if result is not None:
                    return result
            del partial[sid]
            stats["backtracks"] += 1
        return None

    solution = backtrack(domains)
    stats["ms"] = (time.perf_counter() - t0) * 1000
    return solution, stats


def solve_one(problem, rng=None, max_nodes=20000):
    """Cari SATU jadwal valid dengan varian terbaik (MRV + FC). Dipakai solve_all."""
    solution, _ = solve_with_stats(problem, True, True, rng, max_nodes)
    return solution


def solve_all(problem, limit=30, attempts=300, seed=0):
    """Kumpulkan hingga `limit` jadwal valid yang berbeda-beda.
    Urutan nilai domain diacak tiap percobaan supaya hasilnya beragam.
    Mengembalikan list of Schedule. List kosong = tidak ada solusi."""
    rng = random.Random(seed)
    found = {}
    misses = 0
    for _ in range(attempts):
        if len(found) >= limit:
            break
        sol = solve_one(problem, rng)
        if sol is None:
            misses += 1
            if misses >= 5 and not found:
                return []        # kemungkinan besar memang tidak ada solusi
            continue
        found[tuple(sorted(sol.items()))] = sol
    return list(found.values())
