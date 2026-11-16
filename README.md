# AI University Timetable Generator

Sistem penyusun jadwal kuliah (dosen, kelas, ruang, waktu) dengan **CSP** di Python, dibantu
**AI ranking** untuk memilih opsi terbaik, plus skenario tambahan **adversarial search** (war berebut kelas).
Tugas kelompok 5 orang, deadline 3 November 2026.

## Yang dibangun

1. **CSP**: tiap kelas = variabel, domain = (dosen, ruang, slot waktu). Aturan wajib (hard constraint):
   tidak ada bentrok dosen, ruang, atau kelompok mahasiswa; kapasitas ruang cukup; dosen hanya di jam tersedia;
   beban dosen tidak melebihi batas.
2. **Perbandingan algoritma CSP** (`compare.py`): Backtracking biasa vs +MRV vs +Forward Checking vs +MRV+FC.
3. **AI ranking** (`ranking.py`): jadwal valid dinilai dengan soft constraint (preferensi dosen, jeda, sebaran hari,
   hindari sore, kecocokan ruang), lalu diurutkan.
4. **Adversarial search** (`adversarial.py`): dua mahasiswa berebut kelas, diselesaikan dengan minimax dan
   alpha-beta, dibandingkan dengan greedy.
5. **Antarmuka web** (`app.py`, Streamlit).

## Struktur file

| File | Isi | Pemilik |
| --- | --- | --- |
| `models.py` | Struktur data (Section, Lecturer, Room, Slot, Assignment, Problem) | Orang 1 |
| `solver.py` | Solver CSP, 4 varian lewat `solve_with_stats(problem, use_mrv, use_fc)` | Orang 1 |
| `compare.py` | Benchmark perbandingan 4 varian solver | Orang 1 + 5 |
| `dataset.json`, `data.py` | Data dummy dan pemuatnya | Orang 2 |
| `constraints.py` | Semua hard constraint dan validator jadwal | Orang 2 |
| `ranking.py` | Scoring dan pengurutan jadwal (AI ranking) | Orang 3 |
| `adversarial.py` | Minimax, alpha-beta, greedy untuk skenario war | Orang 3 |
| `main.py` | Alur utama (CLI) dan aturan war mahasiswa | Orang 4 |
| `app.py` | UI Streamlit | Orang 4 |
| `tests_scenarios.py` | Skenario uji | Orang 5 |

## Cara menjalankan

```
pip install -r requirements.txt
python main.py                # alur lengkap di terminal
python tests_scenarios.py     # semua tes (harus semua OK)
python compare.py             # benchmark algoritma, sekitar 1 menit
streamlit run app.py          # buka web di browser
```

## Deploy ke web (Streamlit Community Cloud)

1. Taruh semua file di **root** repo GitHub (bukan di dalam subfolder).
2. Buka share.streamlit.io, masuk dengan akun GitHub, klik **New app**.
3. Pilih repo, branch `main`, main file `app.py`, lalu **Deploy**.
4. Tunggu build beberapa menit. Link publik bisa dimasukkan ke PPT.

Catatan: aplikasi gratis bisa "tidur" kalau lama tidak dibuka, jadi buka linknya sebelum presentasi
dan siapkan screenshot cadangan. Jangan jalankan `compare.py` lewat web (butuh sekitar 1 menit).

## Aturan kerja bersama

- Satu orang satu file (lihat tabel). Jangan ubah nama/bentuk fungsi yang dipakai modul lain.
- Kontrak antarmodul:
  - `load_problem(path=None) -> Problem`
  - `build_domain(section, problem) -> list[Assignment]`
  - `is_consistent(section_id, assignment, partial, problem) -> bool`
  - `solve_with_stats(problem, use_mrv, use_fc, rng, max_nodes) -> (Schedule | None, stats)`
  - `solve_all(problem, limit) -> list[Schedule]`
  - `rank(schedules, problem, top_k) -> list[Ranked]`, `explain(ranked, problem) -> str`
  - `jalankan_skenario(schedule, seed_a, seed_b, max_pick, kuota) -> (game, hasil)`
- `Schedule` adalah dict `{section_id: Assignment(lecturer_id, room_id, slot_id)}`.
- Sebelum push: `python tests_scenarios.py` harus semua OK.

## Catatan untuk asisten AI

Proyek ini tugas kuliah (mata kuliah Kecerdasan Buatan). Tujuan penilaiannya: CSP dimodelkan dengan benar,
ada perbandingan antaralgoritma CSP, ada skenario adversarial search, dan sistem bisa didemokan. Kerjakan hanya
file milik orang yang meminta bantuan, pertahankan kontrak fungsi di atas, dan jalankan
`python tests_scenarios.py` setelah mengubah kode.
