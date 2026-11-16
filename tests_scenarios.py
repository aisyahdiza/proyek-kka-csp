"""tests_scenarios.py - skenario uji (dipegang Orang 5).

Jalankan:  python tests_scenarios.py     (atau: pytest tests_scenarios.py)
Tambahkan skenario baru di bawah dan catat hasilnya untuk laporan/PPT.
"""
from dataclasses import replace

from constraints import validate_schedule
from data import load_problem
from main import check_student_selection
from models import Assignment, Room
from ranking import rank
from solver import solve_all


def test_semua_jadwal_valid():
    problem = load_problem()
    schedules = solve_all(problem, limit=10)
    assert schedules, "solver harus menemukan minimal 1 jadwal"
    for sch in schedules:
        assert validate_schedule(sch, problem) == []


def test_ranking_terurut_menurun():
    problem = load_problem()
    ranked = rank(solve_all(problem, limit=20), problem, top_k=5)
    scores = [r.score for r in ranked]
    assert scores == sorted(scores, reverse=True)


def test_tanpa_solusi_kapasitas_kurang():
    problem = load_problem()
    kecil = {rid: Room(rid, r.name, 10) for rid, r in problem.rooms.items()}
    assert solve_all(replace(problem, rooms=kecil)) == []


def test_validator_mendeteksi_bentrok_dosen():
    problem = load_problem()
    sch = {
        "S1": Assignment("D1", "R2", "Sen-08"),
        "S2": Assignment("D1", "R1", "Sen-08"),   # dosen sama, slot sama
    }
    assert any("bentrok" in e for e in validate_schedule(sch, problem))


def test_war_mahasiswa_bentrok_slot():
    problem = load_problem()
    sch = {
        "S1": Assignment("D1", "R2", "Sen-08"),
        "S5": Assignment("D5", "R1", "Sen-08"),
    }
    assert check_student_selection(["S1", "S5"], sch, problem) != []


def test_war_mahasiswa_batas_sks():
    problem = load_problem()
    sch = {"S1": Assignment("D1", "R2", "Sen-08"), "S3": Assignment("D3", "R3", "Sel-08")}
    assert check_student_selection(["S1", "S3"], sch, problem, max_sks=4) != []


def test_semua_varian_solver_menghasilkan_jadwal_valid():
    import random
    from solver import solve_with_stats
    problem = load_problem()
    for mrv in (False, True):
        for fc in (False, True):
            sol, stats = solve_with_stats(problem, mrv, fc, random.Random(0))
            assert sol is not None, f"varian mrv={mrv} fc={fc} harus menemukan solusi"
            assert validate_schedule(sol, problem) == []
            assert stats["nodes"] >= len(problem.sections)


def test_bentrok_kelompok_mahasiswa_terdeteksi():
    problem = load_problem()
    # S1 dan S3 sama-sama kelompok TI-1A, dosen dan ruang berbeda tetapi slot sama
    sch = {
        "S1": Assignment("D1", "R2", "Sen-08"),
        "S3": Assignment("D3", "R3", "Sen-08"),
    }
    assert any("mahasiswa" in e for e in validate_schedule(sch, problem))


def test_solver_tidak_menaruh_kelompok_sama_di_slot_sama():
    problem = load_problem()
    for sch in solve_all(problem, limit=10):
        for a in sch:
            for b in sch:
                if a < b and problem.sections[a].group == problem.sections[b].group:
                    assert sch[a].slot_id != sch[b].slot_id


def _game_demo(max_pick=3, kuota=1):
    from adversarial import jalankan_skenario
    from solver import solve_one
    import random
    problem = load_problem()
    jadwal = solve_one(problem, random.Random(0))
    return jalankan_skenario(jadwal, 1, 2, max_pick, kuota)


def test_alphabeta_nilai_sama_dengan_minimax_tapi_lebih_sedikit_node():
    _, h = _game_demo()
    assert h["nilai_sama"]
    assert h["node_alphabeta"] < h["node_minimax"]


def test_minimax_menjamin_hasil_minimal_nilai_optimal():
    _, h = _game_demo()
    v = h["nilai_optimal"]
    # lawan greedy (tidak optimal) -> A dengan minimax tidak mungkin lebih buruk dari nilai optimal
    assert h["kombinasi"][("minimax", "greedy")]["nilai"] >= v
    # B dengan minimax melawan A greedy -> nilai (A - B) tidak mungkin lebih besar dari nilai optimal
    assert h["kombinasi"][("greedy", "minimax")]["nilai"] <= v


def test_war_adversarial_aturan_pilih_kelas():
    game, _ = _game_demo(max_pick=2)
    state = game.initial()
    langkah, state = game.successors(state)[0]
    assert langkah not in game.legal(state, 0)                    # kelas yang sudah dipilih tidak bisa lagi
    assert langkah not in game.legal(state, 1)                    # kuota 1 sudah habis untuk lawan
    for sid in game.legal(state, 1):                              # kelas sisa tidak boleh sama slot dengan pilihan sendiri
        assert game.slot[sid] not in {game.slot[s] for s in state[1]}


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
            print("OK  ", name)
