"""app.py - antarmuka Streamlit (dipegang Orang 4).

Jalankan lokal :  streamlit run app.py
Deploy         :  lihat README.md (Streamlit Community Cloud, file utama = app.py)
"""
import streamlit as st

from adversarial import jalankan_skenario
from main import check_student_selection, format_schedule, run_pipeline
from ranking import explain

st.set_page_config(page_title="War Jadwal CSP", layout="wide")
st.title("AI University Timetable Generator")
st.caption("CSP (backtracking + MRV + forward checking) untuk menyusun jadwal, "
           "AI ranking untuk memilih opsi terbaik, minimax untuk skenario war.")

if "ranked" not in st.session_state:
    st.session_state.problem, st.session_state.ranked = run_pipeline()

if st.button("Generate ulang jadwal"):
    st.session_state.problem, st.session_state.ranked = run_pipeline()
    st.rerun()

problem = st.session_state.problem
ranked = st.session_state.ranked

if not ranked:
    st.error("Tidak ada jadwal valid untuk data ini.")
    st.stop()

tab_jadwal, tab_adv = st.tabs(["Jadwal dan war mahasiswa", "Skenario adversarial"])

# ---------------------------------------------------------------- tab 1
with tab_jadwal:
    st.subheader("Opsi jadwal terbaik")
    pilihan = st.selectbox("Pilih opsi", range(len(ranked)),
                           format_func=lambda i: f"Peringkat {i + 1} (skor {ranked[i].score})")
    current = ranked[pilihan]
    st.code(format_schedule(current.schedule, problem))
    st.info(explain(current, problem))

    st.subheader("War: pilih kelas yang kamu ambil")
    labels = {sid: f"{problem.sections[sid].course} ({a.slot_id})"
              for sid, a in current.schedule.items()}
    dipilih = st.multiselect("Kelas", list(labels), format_func=lambda s: labels[s])

    if st.button("Konfirmasi pilihan"):
        masalah = check_student_selection(dipilih, current.schedule, problem)
        if masalah:
            for m in masalah:
                st.error(m)
        else:
            st.success("Pilihan kelas berhasil disimpan!")

# ---------------------------------------------------------------- tab 2
with tab_adv:
    st.subheader("Dua mahasiswa berebut kelas (minimax + alpha-beta)")
    st.write("Mahasiswa A dan B bergiliran memilih kelas dari jadwal peringkat 1. "
             "Kuota kelas terbatas, jadi kelas yang diambil A bisa hilang untuk B. "
             "Nilai akhir = total kesukaan A dikurangi total kesukaan B.")
    c1, c2, c3 = st.columns(3)
    max_pick = c1.slider("Kelas per mahasiswa", 1, 4, 3)
    kuota = c2.slider("Kuota tiap kelas", 1, 2, 1)
    seed = c3.number_input("Seed preferensi", 0, 999, 1)

    if st.button("Jalankan skenario"):
        _, h = jalankan_skenario(ranked[0].schedule, int(seed), int(seed) + 1, max_pick, kuota)
        st.metric("Nilai permainan optimal (A - B)", h["nilai_optimal"])
        m1, m2 = st.columns(2)
        m1.metric("Node minimax", h["node_minimax"])
        m2.metric("Node alpha-beta", h["node_alphabeta"])
        baris = [{"Strategi A": sa, "Strategi B": sb, "Nilai (A - B)": r["nilai"],
                  "Kelas A": ", ".join(r["kelas_a"]), "Kelas B": ", ".join(r["kelas_b"])}
                 for (sa, sb), r in h["kombinasi"].items()]
        st.table(baris)
        st.caption("Minimax menjamin hasil terburuk terbaik; greedy cepat tetapi tidak melihat langkah lawan.")
