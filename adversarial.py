"""adversarial.py - skenario tambahan: "war" berebut kelas sebagai permainan dua pemain
(dipegang Orang 3).

Ide: dua mahasiswa (A dan B) bergiliran memilih kelas dari jadwal yang sudah dibuat solver.
Kuota tiap kelas terbatas, jadi kelas yang diambil A bisa hilang untuk B (itu yang membuat ini
permainan "lawan"). Tiap mahasiswa punya nilai kesukaan sendiri untuk tiap kelas.

  - Permainan zero-sum: nilai akhir = (total kesukaan A) - (total kesukaan B)
    A ingin nilai sebesar mungkin (MAX), B ingin sekecil mungkin (MIN).
  - Aturan pilih: kuota kelas masih ada, kelas belum diambil sendiri, tidak bentrok slot
    dengan kelas yang sudah diambil, dan maksimal `max_pick` kelas per mahasiswa.
  - Algoritma: Minimax dan Minimax + Alpha-Beta Pruning (hasil sama, node jauh lebih sedikit),
    dibandingkan dengan strategi greedy (selalu ambil kelas favorit yang masih tersedia).

State permainan = (kelas_A, kelas_B, sisa_kuota, giliran) dengan giliran 0 = A, 1 = B.
"""
import random

INF = float("inf")


def buat_preferensi(section_ids, seed):
    """Nilai kesukaan acak 1..10 untuk tiap kelas (untuk demo). Ganti dengan data asli kalau ada."""
    rng = random.Random(seed)
    return {sid: rng.randint(1, 10) for sid in sorted(section_ids)}


class WarGame:
    def __init__(self, schedule, pref_a, pref_b, seats=None, max_pick=3):
        """schedule: dict section_id -> Assignment (jadwal dari solver).
        seats: dict section_id -> kuota (default 1 per kelas, jadi benar-benar berebut)."""
        self.ids = sorted(schedule)
        self.index = {sid: i for i, sid in enumerate(self.ids)}
        self.slot = {sid: schedule[sid].slot_id for sid in self.ids}
        self.pref = (pref_a, pref_b)
        self.seats0 = tuple((seats or {}).get(sid, 1) for sid in self.ids)
        self.max_pick = max_pick

    def initial(self):
        return ((), (), self.seats0, 0)

    def legal(self, state, player):
        """Kelas yang boleh dipilih `player` pada state ini, urut dari yang paling ia sukai."""
        picks, seats = state[player], state[2]
        if len(picks) >= self.max_pick:
            return []
        used_slots = {self.slot[s] for s in picks}
        moves = [sid for sid in self.ids
                 if seats[self.index[sid]] > 0 and sid not in picks and self.slot[sid] not in used_slots]
        moves.sort(key=lambda s: (-self.pref[player][s], s))   # urutan ini mempercepat alpha-beta
        return moves

    def apply(self, state, sid):
        player = state[3]
        picks = [state[0], state[1]]
        picks[player] = picks[player] + (sid,)
        seats = list(state[2])
        seats[self.index[sid]] -= 1
        return (picks[0], picks[1], tuple(seats), 1 - player)

    def successors(self, state):
        """Daftar (langkah, state_baru). Langkah None = pemain terpaksa lewat giliran.
        List kosong = permainan selesai."""
        player = state[3]
        moves = self.legal(state, player)
        if moves:
            return [(m, self.apply(state, m)) for m in moves]
        if self.legal(state, 1 - player):
            return [(None, (state[0], state[1], state[2], 1 - player))]
        return []

    def utility(self, state):
        return (sum(self.pref[0][s] for s in state[0]) -
                sum(self.pref[1][s] for s in state[1]))


def minimax(game, state, counter):
    """Minimax murni. counter[0] bertambah 1 tiap node yang dikunjungi."""
    counter[0] += 1
    succ = game.successors(state)
    if not succ:
        return game.utility(state), None
    maximizing = state[3] == 0
    best_val, best_move = (-INF if maximizing else INF), None
    for move, nxt in succ:
        v, _ = minimax(game, nxt, counter)
        if (maximizing and v > best_val) or (not maximizing and v < best_val):
            best_val, best_move = v, move
    return best_val, best_move


def alphabeta(game, state, counter, alpha=-INF, beta=INF):
    """Minimax + Alpha-Beta Pruning: memotong cabang yang pasti tidak akan dipilih."""
    counter[0] += 1
    succ = game.successors(state)
    if not succ:
        return game.utility(state), None
    maximizing = state[3] == 0
    best_val, best_move = (-INF if maximizing else INF), None
    for move, nxt in succ:
        v, _ = alphabeta(game, nxt, counter, alpha, beta)
        if maximizing:
            if v > best_val:
                best_val, best_move = v, move
            alpha = max(alpha, best_val)
        else:
            if v < best_val:
                best_val, best_move = v, move
            beta = min(beta, best_val)
        if alpha >= beta:
            break
    return best_val, best_move


def pilih_langkah(game, state, strategi):
    """strategi: 'greedy' (ambil favorit yang tersedia) atau 'minimax' (alpha-beta)."""
    succ = game.successors(state)
    if strategi == "greedy":
        return succ[0]                      # successors sudah urut dari favorit pemain itu
    _, best = alphabeta(game, state, [0])
    for move, nxt in succ:
        if move == best:
            return move, nxt
    return succ[0]


def simulasi(game, strategi_a, strategi_b):
    """Mainkan satu permainan penuh. Mengembalikan dict hasil."""
    state = game.initial()
    strategi = (strategi_a, strategi_b)
    while game.successors(state):
        _, state = pilih_langkah(game, state, strategi[state[3]])
    return {"kelas_a": list(state[0]), "kelas_b": list(state[1]), "nilai": game.utility(state)}


def bandingkan(game):
    """Ringkasan untuk laporan/PPT:
    - nilai permainan optimal + jumlah node minimax vs alpha-beta
    - hasil 4 kombinasi strategi (greedy / minimax untuk A dan B)"""
    c_mm, c_ab = [0], [0]
    v_mm, _ = minimax(game, game.initial(), c_mm)
    v_ab, langkah = alphabeta(game, game.initial(), c_ab)
    kombinasi = {}
    for sa in ("greedy", "minimax"):
        for sb in ("greedy", "minimax"):
            kombinasi[(sa, sb)] = simulasi(game, sa, sb)
    return {
        "nilai_optimal": v_ab,
        "nilai_sama": v_mm == v_ab,
        "node_minimax": c_mm[0],
        "node_alphabeta": c_ab[0],
        "langkah_pertama_a": langkah,
        "kombinasi": kombinasi,
    }


def jalankan_skenario(schedule, seed_a=1, seed_b=2, max_pick=3, kuota=1):
    """Pintu masuk sederhana untuk main.py / app.py. Mengembalikan (game, hasil_bandingkan)."""
    ids = list(schedule)
    game = WarGame(schedule, buat_preferensi(ids, seed_a), buat_preferensi(ids, seed_b),
                   seats={sid: kuota for sid in ids}, max_pick=max_pick)
    return game, bandingkan(game)
