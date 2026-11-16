# My ITS Class Sched : Penyusun Jadwal Kuliah dengan CSP dan AI Ranking

Proyek ini adalah aplikasi web untuk membantu mahasiswa menentukan jadwal kuliah yang **tidak bentrok**. Mahasiswa cukup memilih **maksimal 3 kelas** yang ia inginkan sesuai dengan preferensinya masing-masing. Aplikasi lalu melengkapi sisa mata kuliah dengan kelas yang tidak bentrok dari pilihan tersebut, dengan bantuan AI.

Acuan yang digunakan untuk membuat jadwal ini adalah **jadwal tetap** yang telah disediakan oleh kampus, yaitu jadwal yang sudah memiliki dosen, ruang, hari, dan jam untuk setiap kelasnya. Jadwal tetap ini menjadi variabel yang tidak diubah oleh mahasiswa. Mahasiswa hanya memilih dari kelas-kelas yang sudah ada. 

Web ini dirancang untuk mengatasi masalah mahasiswa yang harus mencari kombinasi jadwal yang cocok secara manual demi mendapatkan jadwal yang tidak tumpang tindih dan sesuai dengan preferensi. Melalui pendekatan **CSP** untuk menjamin jadwal tidak bentrok dan **AI ranking** untuk memilih kombinasi terbaik dari kombinasi yang ada.

Adapun tujuan dari proyek ini adalah:
1. Memungkinkan mahasiswa memilih paling banyak 3 kelas, lalu melengkapi sisanya tanpa bentrok.
2. Mengurutkan hasil berdasarkan kenyamanan jadwal dan preferensi mahasiswa, lalu menampilkan 3 yang terbaik.
3. Membandingkan beberapa varian algoritma pencarian (backtracking biasa, MRV, forward checking).

## Cara kerja

Ada tiga tahap. Hasil tahap sebelumnya menjadi bahan tahap berikutnya.

**Tahap 1: Menyusun jadwal kampus (CSP)**

Data masukan ada di `kampus.py`:

| Data | Isi |
| --- | --- |
| Mata kuliah | Teori Graf (3 SKS), Matematika Diskrit (3), KKA (3), KPPL (2), Pemrograman Web (3), Jaringan Komputer (4), Pemrograman Berbasis Objek (3) |
| Kelas | Tiap mata kuliah punya kelas A, B, dan C, jadi ada 21 kelas |
| Dosen | 6 dosen, masing-masing hanya boleh mengajar mata kuliah tertentu, maksimal 4 kelas per hari |
| Ruangan | Ruang 101 sampai 112 (muat 50 orang), Lab Pemrograman dan Aula Handayani (muat 100 orang) |
| Waktu | Senin sampai Jumat, pukul 07.00 sampai 17.00 |

Satu SKS dihitung satu jam, jadi kelas 3 SKS berlangsung 3 jam berturut-turut dalam satu pertemuan.

CSP memilihkan **dosen, ruang, dan jam** untuk setiap kelas. Aturan yang harus dipenuhi:

- dosen tidak mengajar dua kelas yang jamnya tumpang tindih
- satu ruang tidak dipakai dua kelas pada jam yang tumpang tindih
- kapasitas ruang cukup untuk jumlah mahasiswa
- dosen hanya mengajar mata kuliah yang boleh ia ajar
- dosen mengajar maksimal 4 kelas dalam sehari
- durasi slot sama dengan SKS mata kuliah.

Dengan menggunakan gabungan _backtracking, MRV,_ dan _forward checking_ didapatkan hasil berupa satu jadwal yang tetap. Setiap jadwal akan divalidasi ulangoleh `validate_schedule`. Jadwal juga hanya diterima akalau ternyata masih memungkinkan mahasiswa mengambil semua mata kuliah tanpa bentrok.

**Tahap 2: Mahasiswa memilih kelas**

Dari jadwal tetap tadi, mahasiswa memilih kelas yang ia inginkan, **maksimal 3 kelas**
(satu kelas per mata kulaih). Mata kuliah lainnya `(auto fill)`.  Dengan tambahan bahwa aplikasi akan menolah pilihan yang melanggar aturan, seperti dua kelas bentrok, kuota kelas penuh, atau total SKS melebihi batas.

**Tahap 3: AI ranking melengkapi jadwal**

Untuk mata kuliah yang belum dipilih, program mencari semua kombinasi kelas yang tidak bentrok dengan pilihan mahasiswa (backtracking + MRV + forward checking), lalu memberi skor dan mengurutkannya. Tiga kombinasi jadwal terbaik akan ditampilkan kembali beserta penjelasan singkat akan kelebihan dan kelemahan dari jadwal tersebut.

Skor 0 sampai 100 dihitung dari komponen berikut, beserta bobotnya:
| Komponen | Bobot | Penjelasan |
| -------- | ----- | ---------- |
| Dosen favorit | 0,40 | Kelas yang diajar oleh dosen favorit (opsional) |
| Jeda sedikit | 0,25 | Jam kosong antat kelas pada hari yang sama, makin sedikit makan makin baik |
| Hari kosong | 0,25 | Hari yang diminta agar benar benar kosong (opsional) |
| Hari sedikit | 0,20 | Total hari kuliah sedikit |
| Hindari sore | 0,15 | Kelas yang selesai lewat pukul 15.00 mengurangi skor |

Komponen komponen yang berstatus opsional hanya akan dihitung jika mahasiswa mengisinya dan bobot akan dinormalisasi dari komponen yang aktif.

Contoh: mahasiswa memilih KKA A, Jaringan Komputer B, dan Pemrograman Web C. Program akan mengisi 4 mata kuliah sisanya (Teori Graf, Matematika Diskrit, KPPL, PBO) dengan kelas yang jamnya tidak bentrok, lalu menampilkan 3 kombinasi dengan skor tertinggi.

## Cara menjalankan

```
pip install -r requirements.txt
python kampus.py              # lihat jadwal tetap hasil CSP di terminal
streamlit run app.py          # aplikasi web lengkap
python tests_scenarios.py     # jalankan semua tes
```

Atau langsung membukanya versi online: https://kkaminiproject-jrqusj4gsebacjzctffu6k.streamlit.app/


Aplikasi ini memiliki dua tab yang ditawarkan, yang pertama **Data dan jadwal CSP** untuk mendapatkan jadwal tetap dan yang kedua **Pilih kelas dan AI ranking** untuk memilih maksimal 3 kelas, isi preferensi, lalu cari jadwal terbaik. Tombol "Generate ulang jadwal CSP" membuat jadwal tetap yang baru.

## Isi file

| File | Fungsi |
| ---- | ------ |
| `app.py` | Tampilan web dengan Streamlit |
| `kampus.py` | Data kampus dan pembuatan jadwal tetap lewat CSP |
| `krs.py` | Pilihan mahasiswa dan AI ranking |
| `solver.py` | Solver CSP empat varian melewati `solver_with_stats(problem, user_mrv, use_fc) |
| `constraints.py` | Semua aturan wajib dan validator jadwal |
| `models.py` | Struktur data (Section, Lecturer, Room, Slot, Assignment, Problem) |
| `ranking.py` | Skor dan urutan jadwal untuk datatest lama |
| `compare.py`, `benchmark.py` | Perbandingan backtracking biasa, +MRV, +Forward Checking, dan +MRV+FC |
| `main.py`, `data.py`, `dataset*.json` | Alur CLI dan dataset contoh yang lebih kecil untuk pengujian dan perbandingan |
| `gen_dataset.py` | Pembuat dataset acak untuk benchmark |
| `tests_scenarios.py` | Skenario uji |

## Mengubah data

Semua data kampus ada di bagian atas `kampus.py`: daftar `MATKUL`, `DOSEN`, `RUANGAN`, jam kuliah, dan `KELAS_PER_MATKUL`. Untuk mengubahnya bisa dilakukan di sana. Batas 3 pilihan mahasiswa ada di `MAKS_PILIHAN` pada `app.py`.
