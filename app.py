import streamlit as st
import cv2
import numpy as np
import os
import pandas as pd
from PIL import Image
from datetime import datetime

from src.config import (
    SAMPLE_FACES_DIR,
    EVAL_RESULTS_DIR,
    LBP_SIMILARITY_THRESHOLD,
    FACE_TARGET_SIZE
)
from src.database import DatabaseManager
from src.detector import FaceDetector
from src.preprocessing import ImagePreprocessor
from src.feature_extractor import LBPHFeatureExtractor
from src.boarding_engine import BoardingGateEngine
from src.evaluator import SystemEvaluator
from src.seed_data import seed_database

# ---------------------------------------------------------
# Konfigurasi Halaman Streamlit
# ---------------------------------------------------------
st.set_page_config(
    page_title="KAI Face Recognition Boarding Gate",
    page_icon="🚄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS Korporat Kereta Api Indonesia (KAI)
st.markdown("""
<style>
    /* Warna Utama KAI */
    :root {
        --kai-navy: #1E2B58;
        --kai-orange: #ED6B23;
        --kai-light-blue: #0077B6;
    }
    .main-header {
        background: linear-gradient(135deg, #1E2B58 0%, #0D1630 100%);
        padding: 20px 28px;
        border-radius: 12px;
        color: white;
        margin-bottom: 25px;
        border-left: 8px solid #ED6B23;
        box-shadow: 0 4px 15px rgba(0,0,0,0.15);
    }
    .main-header h1 {
        color: #FFFFFF;
        font-size: 26px;
        margin: 0;
        font-weight: 700;
    }
    .main-header p {
        color: #E0E0E0;
        margin: 5px 0 0 0;
        font-size: 14px;
    }
    .gate-card-granted {
        background-color: #E8F5E9;
        border: 2px solid #2E7D32;
        border-radius: 10px;
        padding: 16px;
        color: #1B5E20;
    }
    .gate-card-denied {
        background-color: #FFEBEE;
        border: 2px solid #C62828;
        border-radius: 10px;
        padding: 16px;
        color: #B71C1C;
    }
    .gate-card-waiting {
        background-color: #FFF3E0;
        border: 2px solid #EF6C00;
        border-radius: 10px;
        padding: 16px;
        color: #E65100;
    }
    .metric-badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: bold;
        font-size: 12px;
    }
    .ticket-card {
        background: #FFFFFF;
        border: 1px solid #E0E0E0;
        border-radius: 10px;
        padding: 18px;
        border-top: 4px solid #1E2B58;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Inisialisasi Layanan & Session State
# ---------------------------------------------------------
@st.cache_resource
def get_db():
    return DatabaseManager()

@st.cache_resource
def get_engine():
    return BoardingGateEngine(threshold=LBP_SIMILARITY_THRESHOLD)

@st.cache_resource
def get_preprocessor():
    return ImagePreprocessor()

@st.cache_resource
def get_extractor():
    return LBPHFeatureExtractor()

@st.cache_resource
def get_evaluator():
    return SystemEvaluator()

db = get_db()
engine = get_engine()
preprocessor = get_preprocessor()
extractor = get_extractor()
evaluator = get_evaluator()

# ---------------------------------------------------------
# Sidebar Menu
# ---------------------------------------------------------
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/5/56/Logo_PT_Kereta_Api_Indonesia_%28Persero%29_2020.svg", width=180)
    st.markdown("### **Smart Station Gate**")
    st.markdown("---")
    
    menu = st.radio(
        "Pilih Menu:",
        [
            "🚄 Simulasi Boarding Gate",
            "🔬 Pipeline Pengolahan Citra",
            "👤 Registrasi Wajah Penumpang",
            "📊 Evaluasi & Metrik Sistem",
            "📋 Manifest & Log Audit Gate"
        ]
    )

    st.markdown("---")
    st.markdown("#### **Pengaturan Parameter Gate**")
    current_threshold = st.slider(
        "Ambang Batas Chi-Square (Threshold)",
        min_value=0.15,
        max_value=0.45,
        value=float(LBP_SIMILARITY_THRESHOLD),
        step=0.01,
        help="Semakin kecil threshold, sistem semakin ketat menolak orang asing (FRR naik, FAR turun)."
    )
    engine.set_threshold(current_threshold)

    selected_gate = st.selectbox("Pilih Unit Gate:", ["GATE-01 (Utara)", "GATE-02 (Selatan)", "GATE-VIP"])

    if st.button("🔄 Reset Tiket Demo (Kembalikan ke ACTIVE)"):
        with db._get_connection() as conn:
            conn.execute("UPDATE tickets SET status_tiket = 'ACTIVE', waktu_boarding = NULL")
            conn.commit()
        st.success("Seluruh tiket demo berhasil di-reset!")
        st.rerun()

# ---------------------------------------------------------
# Header Aplikasi
# ---------------------------------------------------------
st.markdown("""
<div class="main-header">
    <h1>🚄 SISTEM BOARDING GATE OTOMATIS BERBASIS PENGENALAN WAJAH</h1>
    <p>Implementasi Metode Pengolahan Citra Digital (Viola-Jones, CLAHE, dan Local Binary Pattern Histogram) pada Sistem Tiketing PT Kereta Api Indonesia (Persero)</p>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# MENU 1: SIMULASI BOARDING GATE
# ---------------------------------------------------------
if menu == "🚄 Simulasi Boarding Gate":
    st.subheader("🎥 Pemindaian Wajah di Pintu Masuk Peron (Boarding Gate)")
    
    col_input, col_result = st.columns([1.1, 1.2])

    with col_input:
        input_mode = st.radio(
            "Pilih Sumber Masukan Citra:",
            ["Pilih Sampel Penumpang KAI", "Unggah Citra Manual", "Kamera Langsung (Webcam)"],
            horizontal=True
        )

        test_image_bgr = None

        if input_mode == "Pilih Sampel Penumpang KAI":
            sample_files = [f for f in os.listdir(SAMPLE_FACES_DIR) if f.endswith(".jpg")]
            selected_file = st.selectbox(
                "Pilih Profil Penumpang untuk Disimulasikan:",
                sample_files,
                format_func=lambda x: "👤 " + x.replace(".jpg", "").replace("_", " ").title()
            )
            if selected_file:
                img_path = os.path.join(SAMPLE_FACES_DIR, selected_file)
                test_image_bgr = cv2.imread(img_path)
                st.image(cv2.cvtColor(test_image_bgr, cv2.COLOR_BGR2RGB), caption=f"Pratinjau: {selected_file}", width=260)

        elif input_mode == "Unggah Citra Manual":
            uploaded_file = st.file_uploader("Unggah Foto Wajah (JPG / PNG):", type=["jpg", "jpeg", "png"])
            if uploaded_file is not None:
                file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
                test_image_bgr = cv2.imdecode(file_bytes, 1)
                st.image(cv2.cvtColor(test_image_bgr, cv2.COLOR_BGR2RGB), caption="Citra Diunggah", width=280)

        elif input_mode == "Kamera Langsung (Webcam)":
            camera_img = st.camera_input("Arahkan wajah ke webcam:")
            if camera_img is not None:
                file_bytes = np.asarray(bytearray(camera_img.read()), dtype=np.uint8)
                test_image_bgr = cv2.imdecode(file_bytes, 1)

    with col_result:
        st.markdown("#### **Hasil Verifikasi Smart Gate**")

        if test_image_bgr is not None:
            # Jalankan Mesin Boarding KAI
            res = engine.process_frame(test_image_bgr, gate_id=selected_gate)

            # Tampilkan Banner Status Pintu Gate
            gate_status = res["gate_status"]
            if gate_status == "GRANTED":
                st.markdown(f"""
                <div class="gate-card-granted">
                    <h3 style="margin:0;">✅ PINTU TERBUKA (GATE OPEN)</h3>
                    <p style="margin:5px 0 0 0; font-size:15px;">{res['message']}</p>
                </div>
                """, unsafe_allow_html=True)
            elif gate_status == "DENIED":
                st.markdown(f"""
                <div class="gate-card-denied">
                    <h3 style="margin:0;">⛔ PINTU TERKUNCI (ACCESS DENIED)</h3>
                    <p style="margin:5px 0 0 0; font-size:15px;">{res['message']}</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="gate-card-waiting">
                    <h3 style="margin:0;">⏳ MENUNGGU PENUMPANG</h3>
                    <p style="margin:5px 0 0 0; font-size:15px;">{res['message']}</p>
                </div>
                """, unsafe_allow_html=True)

            # Tampilkan Frame Teranotasi
            st.image(
                cv2.cvtColor(res["annotated_frame"], cv2.COLOR_BGR2RGB),
                caption=f"Frame Sensor Kamera ({selected_gate})",
                use_container_width=True
            )

            # Metrik Komputasi
            m = res["metrics"]
            m_col1, m_col2, m_col3 = st.columns(3)
            m_col1.metric("Waktu Komputasi", f"{m['latency_ms']:.1f} ms")
            m_col2.metric("Distance Score", f"{m['distance']:.4f}")
            m_col3.metric("Kecocokan (Confidence)", f"{m['confidence']:.1f}%")

            # Tiket Penumpang Terverifikasi
            ticket = res.get("ticket")
            passenger = res.get("passenger")
            if passenger and ticket:
                st.markdown("---")
                st.markdown("#### 🎫 **Boarding Pass Elektronik (E-Ticket KAI)**")
                st.markdown(f"""
                <div class="ticket-card">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <span style="font-weight:bold; color:#1E2B58; font-size:18px;">{ticket['nama_kereta']}</span>
                        <span style="background:#ED6B23; color:white; padding:3px 10px; border-radius:5px; font-weight:bold;">
                            {ticket['ticket_code']}
                        </span>
                    </div>
                    <hr style="margin:10px 0;">
                    <p style="margin:4px 0;"><strong>Nama Penumpang:</strong> {passenger['nama']}</p>
                    <p style="margin:4px 0;"><strong>NIK:</strong> {passenger['nik']}</p>
                    <p style="margin:4px 0;"><strong>Relasi:</strong> {ticket['relasi']}</p>
                    <p style="margin:4px 0;"><strong>Jadwal Keberangkatan:</strong> {ticket['jadwal_berangkat']}</p>
                    <p style="margin:4px 0;"><strong>Nomor Kursi:</strong> <span style="font-size:16px; color:#0077B6; font-weight:bold;">{ticket['gerbong_kursi']}</span></p>
                    <p style="margin:4px 0;"><strong>Status Boarding:</strong> <span style="color:green; font-weight:bold;">TERVERIFIKASI WAJAH</span></p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Arahkan webcam atau pilih foto sampel di panel sebelah kiri untuk memulai pemindaian boarding gate.")

# ---------------------------------------------------------
# MENU 2: PIPELINE PENGOLAHAN CITRA
# ---------------------------------------------------------
elif menu == "🔬 Pipeline Pengolahan Citra":
    st.subheader("🔬 Visualisasi Mendalam Pipeline Pengolahan Citra Digital")
    st.markdown("""
    Halaman ini mendemonstrasikan transformasi citra digital tahap demi tahap
    dari akuisisi citra sensor mentah hingga ekstraksi ciri deskriptor spasial **LBPH (Local Binary Pattern Histogram)**.
    """)

    sample_files = [f for f in os.listdir(SAMPLE_FACES_DIR) if f.endswith(".jpg")]
    sel_img_name = st.selectbox("Pilih Citra Subjek Uji:", sample_files)
    
    if sel_img_name:
        img_bgr = cv2.imread(os.path.join(SAMPLE_FACES_DIR, sel_img_name))
        stages = preprocessor.get_intermediate_stages(img_bgr)
        norm_face = stages["6. Normalisasi Ukuran (128x128)"]
        lbp_map = extractor.compute_lbp_image(norm_face)
        stages["7. Peta Tekstur Spasial (LBP 2D)"] = lbp_map

        # Tampilkan galeri tahapan
        cols = st.columns(len(stages))
        for idx, (title, s_img) in enumerate(stages.items()):
            with cols[idx]:
                if len(s_img.shape) == 3:
                    st.image(cv2.cvtColor(s_img, cv2.COLOR_BGR2RGB), use_container_width=True)
                else:
                    st.image(s_img, use_container_width=True, clamp=True)
                st.caption(f"**{title}**")

        st.markdown("---")
        st.markdown("### 📐 **Penjelasan Matematis Metode yang Diterapkan**")

        tab_gray, tab_clahe, tab_lbp, tab_chi = st.tabs([
            "1. Grayscale & Filter Bilateral",
            "2. Normalisasi Kontras (CLAHE)",
            "3. Deskriptor Tekstur (LBPH)",
            "4. Metrik Chi-Square Distance"
        ])

        with tab_gray:
            st.markdown(r"""
            #### Konversi Grayscale & Filter Bilateral
            - **Grayscale (ITU-R BT.601)**:
              $$I_{\text{gray}} = 0.299 \cdot R + 0.587 \cdot G + 0.114 \cdot B$$
              Mereduksi dimensi ruang warna dari 3 kanal RGB menjadi 1 kanal luminansi tanpa kehilangan informasi tepi.
            - **Bilateral Filtering**:
              $$I^{\text{filtered}}(x) = \frac{1}{W_p} \sum_{x_i \in \Omega} I(x_i) f_r(\|I(x_i) - I(x)\|) g_s(\|x_i - x\|)$$
              Menghaluskan derau kulit seragam namun **mempertahankan ketajaman tepi kontur mata, bibir, dan hidung**.
            """)

        with tab_clahe:
            st.markdown(r"""
            #### Contrast Limited Adaptive Histogram Equalization (CLAHE)
            - Citra dibagi menjadi kisi-kisi ubin kontekstual ($8 \times 8$).
            - Setiap ubin diekualisasi secara lokal dengan ambang batas pemotongan (*clip limit* = 2.5) untuk mencegah amplifikasi *noise*.
            - Transformasi antar ubin diinterpolasi secara bilinear untuk menghilangkan efek garis batas ubin.
            - **Manfaat Nyata:** Mengatasi variasi pencahayaan ekstrem pada pintu peron stasiun kereta (bayangan tajam atau lampu sorot LED).
            """)

        with tab_lbp:
            st.markdown(r"""
            #### Ekstraksi Ciri Local Binary Pattern (LBP)
            Untuk setiap piksel pusat $(x_c, y_c)$ dengan 8 piksel tetangga $(i_p)$:
            $$LBP(x_c, y_c) = \sum_{p=0}^{7} s(i_p - i_c) \cdot 2^p, \quad \text{di mana } s(x) = \begin{cases} 1, & x \ge 0 \\ 0, & x < 0 \end{cases}$$
            - Citra dinormalisasi dibagi menjadi $8 \times 8 = 64$ sel grid lokal.
            - Setiap sel memiliki histogram 256 bin tekstur.
            - Vektor fitur global dibentuk melalui konkatenasi seluruh histogram sel:
              $$\text{Panjang Vektor} = 8 \times 8 \times 256 = 16.384 \text{ fitur bertingkat spasial.}$$
            """)

        with tab_chi:
            st.markdown(r"""
            #### Pencocokan Biometrik Chi-Square Distance
            Untuk membandingkan kemiripan antara dua histogram tekstur $H_1$ dan $H_2$:
            $$D_{\chi^2}(H_1, H_2) = \frac{1}{2} \sum_{i} \frac{(H_1(i) - H_2(i))^2}{H_1(i) + H_2(i) + \epsilon}$$
            - Jika $D_{\chi^2} < \text{Threshold}$ (default = 0.28): **Wajah Cocok (Genuine Passenger)**.
            - Jika $D_{\chi^2} \ge \text{Threshold}$: **Wajah Berbeda (Impostor / Ditolak)**.
            """)

# ---------------------------------------------------------
# MENU 3: REGISTRASI WAJAH PENUMPANG
# ---------------------------------------------------------
elif menu == "👤 Registrasi Wajah Penumpang":
    st.subheader("👤 Kios Pendaftaran Face Recognition Penumpang (Enrolment)")
    st.markdown("Pendaftaran profil biometrik wajah penumpang untuk dapat menggunakan fasilitas Smart Boarding Gate KAI.")

    col_form, col_cam = st.columns([1, 1])

    with col_form:
        nik_input = st.text_input("Nomor Induk Kependudukan (NIK 16 Digit):", value="3273012309990006")
        nama_input = st.text_input("Nama Lengkap Penumpang:", value="Bambang Wijaya")
        gender_input = st.selectbox("Jenis Kelamin:", ["Laki-laki", "Perempuan"])
        telp_input = st.text_input("Nomor Telepon / WhatsApp:", value="081298765432")

        st.markdown("##### **Data Tiket Perjalanan Perdana**")
        kereta_input = st.selectbox(
            "Kereta Api:",
            ["Argo Parahyangan (KA 35)", "Taksaka (KA 68)", "Argo Bromo Anggrek (KA 2)", "Lodaya (KA 92)", "Turangga (KA 65)"]
        )
        relasi_input = st.selectbox(
            "Relasi Stasiun:",
            ["Gambir (GMR) - Bandung (BD)", "Gambir (GMR) - Yogyakarta (YK)", "Gambir (GMR) - Surabaya Pasarturi (SBI)", "Bandung (BD) - Solo Balapan (SLO)"]
        )
        kursi_input = st.text_input("Nomor Kursi:", value="Eksekutif 2 / 7A")
        ticket_code = "KAI-" + str(np.random.randint(100000, 999999))

    with col_cam:
        st.markdown("##### **Pengambilan Foto Wajah Referensi**")
        reg_cam = st.camera_input("Ambil Foto Wajah Penumpang:")
        reg_file = st.file_uploader("Atau Unggah Foto Wajah (JPG / PNG):", type=["jpg", "png", "jpeg"], key="reg_upload")

        reg_img_bgr = None
        if reg_cam is not None:
            fb = np.asarray(bytearray(reg_cam.read()), dtype=np.uint8)
            reg_img_bgr = cv2.imdecode(fb, 1)
        elif reg_file is not None:
            fb = np.asarray(bytearray(reg_file.read()), dtype=np.uint8)
            reg_img_bgr = cv2.imdecode(fb, 1)

        if st.button("💾 Daftarkan Wajah & Terbitkan Tiket", type="primary"):
            if not nik_input or not nama_input:
                st.error("Mohon lengkapi NIK dan Nama Penumpang!")
            elif reg_img_bgr is None:
                st.error("Silakan ambil atau unggah foto wajah terlebih dahulu!")
            else:
                # Deteksi dan simpan template
                detector = FaceDetector()
                _, face_roi = detector.detect_primary_face(reg_img_bgr)
                if face_roi is None:
                    face_roi = reg_img_bgr

                prep_roi = preprocessor.process(face_roi)
                feat = extractor.extract_features(prep_roi)

                # Simpan foto ke disk
                fname = f"{nik_input}_{nama_input.replace(' ', '_').lower()}.jpg"
                fpath = os.path.join(SAMPLE_FACES_DIR, fname)
                cv2.imwrite(fpath, reg_img_bgr)

                # Simpan ke DB
                db.save_passenger(nik_input, nama_input, gender_input, telp_input, fpath)
                db.save_face_template(nik_input, "LBPH", feat)
                
                jadwal_now = (datetime.now()).strftime("%Y-%m-%d %H:%M:%S")
                db.save_ticket(ticket_code, nik_input, kereta_input, relasi_input, jadwal_now, kursi_input, "ACTIVE")

                st.success(f"🎉 Penumpang **{nama_input}** (NIK: {nik_input}) berhasil didaftarkan!")
                st.info(f"Kode Tiket: **{ticket_code}** | Status: **ACTIVE**")

# ---------------------------------------------------------
# MENU 4: EVALUASI & METRIK SISTEM
# ---------------------------------------------------------
elif menu == "📊 Evaluasi & Metrik Sistem":
    st.subheader("📊 Evaluasi Kinerja dan Analisis Kuantitatif Sistem")
    st.markdown("""
    Modul evaluasi ini menguji performa sistem berdasarkan ketentuan pengujian resmi Bagian 9 dokumen tugas:
    - **Metrik Klasifikasi Biometrik**: Accuracy, Precision, Recall, F1-Score, False Acceptance Rate (FAR), dan False Rejection Rate (FRR).
    - **Ketahanan Lingkungan**: Evaluasi pada kondisi normal, redup (dim), silau (bright), derau sensor, dan rotasi sudut kepala.
    """)

    if st.button("🚀 Jalankan Pengujian Otomatis (Benchmark Suite)", type="primary"):
        with st.spinner("Menjalankan benchmark biometrik komprehensif pada dataset..."):
            samples = {}
            for f in os.listdir(SAMPLE_FACES_DIR):
                if f.endswith(".jpg") and not f.startswith("impostor"):
                    p_name = f.replace(".jpg", "")
                    samples[p_name] = cv2.imread(os.path.join(SAMPLE_FACES_DIR, f))

            res = evaluator.run_benchmark_suite(samples, threshold=current_threshold)
            st.session_state["benchmark_results"] = res
            st.success("Pengujian benchmark selesai!")

    # Tampilkan hasil
    cm_path = os.path.join(EVAL_RESULTS_DIR, "confusion_matrix.png")
    robust_path = os.path.join(EVAL_RESULTS_DIR, "condition_robustness.png")
    curve_path = os.path.join(EVAL_RESULTS_DIR, "far_frr_curve.png")
    latency_path = os.path.join(EVAL_RESULTS_DIR, "latency_breakdown.png")
    csv_path = os.path.join(EVAL_RESULTS_DIR, "evaluasi_metrik.csv")

    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
        st.markdown("#### **Tabel Metrik Kinerja Pengenalan Wajah**")
        st.dataframe(df, use_container_width=True)

        m_col1, m_col2, m_col3, m_col4 = st.columns(4)
        m_col1.metric("Akurasi Sistem", df["Akurasi"].iloc[0])
        m_col2.metric("Presisi", df["Presisi"].iloc[0])
        m_col3.metric("Recall (Sensitivity)", df["Recall"].iloc[0])
        m_col4.metric("F1-Score", df["F1-Score"].iloc[0])

        st.markdown("---")
        st.markdown("#### **Grafik Evaluasi Akademik**")

        g_col1, g_col2 = st.columns(2)
        with g_col1:
            if os.path.exists(cm_path):
                st.image(cm_path, caption="1. Confusion Matrix Pengujian Biometrik", use_container_width=True)
            if os.path.exists(robust_path):
                st.image(robust_path, caption="2. Ketahanan Pengenalan terhadap Kondisi Stasiun", use_container_width=True)

        with g_col2:
            if os.path.exists(curve_path):
                st.image(curve_path, caption="3. Kurva FAR vs FRR & Ambang Batas Optimal (EER)", use_container_width=True)
            if os.path.exists(latency_path):
                st.image(latency_path, caption="4. Perincian Waktu Eksekusi Pipeline (Latency Breakdown)", use_container_width=True)

# ---------------------------------------------------------
# MENU 5: MANIFEST & LOG AUDIT GATE
# ---------------------------------------------------------
elif menu == "📋 Manifest & Log Audit Gate":
    st.subheader("📋 Manifest Penumpang & Catatan Audit Log Pintu Gate")

    tab_manifest, tab_logs = st.tabs(["Manifest Penumpang Terdaftar", "Catatan Audit Log Smart Gate"])

    with tab_manifest:
        passengers = db.get_all_passengers_with_tickets()
        if passengers:
            df_p = pd.DataFrame(passengers)
            st.dataframe(df_p, use_container_width=True)
        else:
            st.info("Belum ada data manifest penumpang.")

    with tab_logs:
        logs = db.get_recent_logs(limit=100)
        if logs:
            df_logs = pd.DataFrame(logs)
            st.dataframe(df_logs, use_container_width=True)
        else:
            st.info("Belum ada transaksi boarding yang tercatat.")
