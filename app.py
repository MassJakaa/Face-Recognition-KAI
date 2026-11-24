import streamlit as st
import cv2
import numpy as np
import os
import pandas as pd
from PIL import Image
from datetime import datetime, date, time

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

# ---------------------------------------------------------
# Konfigurasi Halaman Streamlit
# ---------------------------------------------------------
st.set_page_config(
    page_title="KAI Smart Boarding Gate & Ticket System",
    page_icon="🚄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS Korporat PT Kereta Api Indonesia (Persero)
st.markdown("""
<style>
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
    .ticket-card {
        background: #FFFFFF;
        border: 1px solid #E0E0E0;
        border-radius: 10px;
        padding: 18px;
        border-top: 4px solid #1E2B58;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    }
    .account-badge {
        background: #E3F2FD;
        border: 1px solid #90CAF9;
        border-radius: 8px;
        padding: 10px 14px;
        color: #0D47A1;
        margin-bottom: 12px;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Inisialisasi Layanan & Resource
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
def get_detector():
    return FaceDetector()

@st.cache_resource
def get_evaluator():
    return SystemEvaluator()

db = get_db()
engine = get_engine()
preprocessor = get_preprocessor()
extractor = get_extractor()
detector = get_detector()
evaluator = get_evaluator()

# ---------------------------------------------------------
# Sidebar Menu
# ---------------------------------------------------------
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/5/56/Logo_PT_Kereta_Api_Indonesia_%28Persero%29_2020.svg", width=180)
    st.markdown("### **Smart Station Gate**")
    st.caption("Sistem Tiketing & Biometrik KAI")
    st.markdown("---")
    
    menu = st.radio(
        "Alur Proses KAI:",
        [
            "1. 👤 Registrasi Akun & Wajah",
            "2. 🎫 Pemesanan Tiket (Booking)",
            "3. 🚄 Simulasi Boarding Gate",
            "4. 🔬 Pipeline Pengolahan Citra",
            "5. 📊 Evaluasi & Metrik Sistem",
            "6. 📋 Data Manifest & Audit Log"
        ]
    )

    st.markdown("---")
    st.markdown("#### **Pengaturan Parameter Gate**")
    current_threshold = st.slider(
        "Ambang Batas Chi-Square (Threshold)",
        min_value=0.15,
        max_value=0.35,
        value=float(LBP_SIMILARITY_THRESHOLD),
        step=0.01,
        help="Semakin kecil threshold, sistem semakin ketat menolak orang asing (FRR naik, FAR turun)."
    )
    engine.set_threshold(current_threshold)

    selected_gate = st.selectbox("Pilih Unit Gate:", ["GATE-01 (Utara)", "GATE-02 (Selatan)", "GATE-VIP"])

    if st.button("🔄 Reset Tiket Demo (Kembalikan ke ACTIVE)"):
        with db._get_connection() as conn:
            conn.execute("UPDATE tickets SET status_tiket = 'ACTIVE', waktu_boarding = NULL WHERE nik != '3578021509950003'")
            conn.commit()
        st.success("Seluruh tiket demo berhasil di-reset!")
        st.rerun()

# ---------------------------------------------------------
# Header Utama
# ---------------------------------------------------------
st.markdown("""
<div class="main-header">
    <h1>🚄 SISTEM SMART BOARDING GATE PT KERETA API INDONESIA</h1>
    <p>Alur Lengkap KAI: Registrasi Akun Berbasis Wajah (Enrolment) ➔ Pemesanan Tiket Tanpa Foto Ulang (Booking) ➔ Verifikasi Masuk Peron Otomatis (Boarding)</p>
</div>
""", unsafe_allow_html=True)

# =========================================================
# MENU 1: REGISTRASI AKUN & PEREKAMAN WAJAH (KAI ENROLMENT)
# =========================================================
if menu == "1. 👤 Registrasi Akun & Wajah":
    st.subheader("👤 Langkah 1: Pendaftaran Akun Baru & Perekaman Biometrik Wajah")
    st.markdown("""
    Seperti pada kios registrasi *Face Recognition* di stasiun atau aplikasi *Access by KAI*, 
    penumpang mendaftarkan akun **satu kali** menggunakan e-KTP dan foto wajah. 
    Wajah yang didaftarkan akan disimpan dalam bentuk template biometrik terenkripsi untuk seluruh perjalanan selanjutnya.
    """)

    col_form, col_photo = st.columns([1.1, 1.2])

    with col_form:
        st.markdown("##### **1. Informasi Identitas Diri (e-KTP)**")
        nik_reg = st.text_input("Nomor Induk Kependudukan (NIK 16 Digit):", placeholder="Contoh: 3273012809980007")
        nama_reg = st.text_input("Nama Lengkap (Sesuai KTP):", placeholder="Contoh: Muhammad Ihsan")
        gender_reg = st.selectbox("Jenis Kelamin:", ["Laki-laki", "Perempuan"])
        telp_reg = st.text_input("Nomor Handphone / WhatsApp:", placeholder="Contoh: 081234567890")

        # Cek apakah NIK sudah pernah terdaftar
        if nik_reg and len(nik_reg) >= 5:
            existing = db.get_passenger(nik_reg)
            if existing:
                st.warning(f"⚠️ NIK {nik_reg} sudah terdaftar atas nama **{existing['nama']}**. Jika mendaftar ulang, data wajah akan diperbarui.")

    with col_photo:
        st.markdown("##### **2. Perekaman Citra Wajah (Biometric Enrolment)**")
        photo_mode = st.radio("Pilih Metode Pengambilan Foto Wajah:", ["Gunakan Kamera (Webcam)", "Unggah Foto Asli (JPG/PNG)"], horizontal=True)

        face_input_bgr = None
        if photo_mode == "Gunakan Kamera (Webcam)":
            cam_shot = st.camera_input("Arahkan wajah lurus ke kamera:")
            if cam_shot is not None:
                bytes_arr = np.asarray(bytearray(cam_shot.read()), dtype=np.uint8)
                face_input_bgr = cv2.imdecode(bytes_arr, 1)
        else:
            up_shot = st.file_uploader("Pilih file foto wajah pasfoto:", type=["jpg", "png", "jpeg"])
            if up_shot is not None:
                bytes_arr = np.asarray(bytearray(up_shot.read()), dtype=np.uint8)
                face_input_bgr = cv2.imdecode(bytes_arr, 1)
                st.image(cv2.cvtColor(face_input_bgr, cv2.COLOR_BGR2RGB), caption="Pratinjau Foto Wajah", width=220)

        # Tombol Pendaftaran Akun
        if st.button("💾 Daftarkan Akun & Rekam Wajah", type="primary", use_container_width=True):
            if not nik_reg or not nama_reg:
                st.error("Mohon lengkapi NIK dan Nama Lengkap!")
            elif face_input_bgr is None:
                st.error("Silakan ambil foto atau unggah gambar wajah terlebih dahulu!")
            else:
                with st.spinner("Memproses deteksi wajah, CLAHE, dan ekstraksi ciri LBPH..."):
                    # 1. Deteksi Wajah ROI
                    bbox, face_roi = detector.detect_primary_face(face_input_bgr)
                    if face_roi is None:
                        face_roi = face_input_bgr

                    # 2. Prapemrosesan Citra Digital
                    prep_face = preprocessor.process(face_roi)

                    # 3. Ekstraksi Vektor Fitur LBPH
                    feature_vec = extractor.extract_features(prep_face)

                    # 4. Simpan Citra ke Folder Sample Faces
                    fname = f"{nik_reg}_{nama_reg.replace(' ', '_').lower()}.jpg"
                    fpath = os.path.join(SAMPLE_FACES_DIR, fname)
                    cv2.imwrite(fpath, face_input_bgr)

                    # 5. Simpan ke Basis Data
                    db.save_passenger(nik_reg, nama_reg, gender_reg, telp_reg, fpath)
                    db.save_face_template(nik_reg, "LBPH", feature_vec)

                    st.success(f"🎉 Akun atas nama **{nama_reg}** (NIK: {nik_reg}) berhasil didaftarkan!")
                    st.info("Wajah biometrik Anda kini telah tersimpan di sistem KAI. Saat memesan tiket di menu berikutnya, Anda **tidak perlu mengunggah foto lagi**!")

# =========================================================
# MENU 2: PEMESANAN TIKET KERETA (KAI TICKET BOOKING)
# =========================================================
elif menu == "2. 🎫 Pemesanan Tiket (Booking)":
    st.subheader("🎫 Langkah 2: Pemesanan Tiket Kereta Api (Booking)")
    st.markdown("""
    Pada tahap pemesanan tiket, Anda **cukup memasukkan NIK dan Nama**. 
    Sistem akan otomatis menautkan tiket perjalanan ini ke profil biometrik wajah yang sudah didaftarkan pada Langkah 1!
    """)

    col_book_left, col_book_right = st.columns([1.1, 1.2])

    with col_book_left:
        st.markdown("##### **1. Identifikasi Penumpang**")
        
        # Pilihan cepat dari daftar akun terdaftar atau input manual
        registered_accounts = db.get_all_passengers()
        account_options = ["-- Masukkan NIK & Nama Manual --"] + [f"{acc['nama']} (NIK: {acc['nik']})" for acc in registered_accounts]
        
        selected_account_opt = st.selectbox("Pilih Akun Penumpang Terdaftar (Quick Select):", account_options)

        nik_val = ""
        nama_val = ""

        if selected_account_opt != "-- Masukkan NIK & Nama Manual --":
            # Extract NIK
            sel_nik = selected_account_opt.split("(NIK: ")[1].replace(")", "")
            sel_acc = db.get_passenger(sel_nik)
            if sel_acc:
                nik_val = sel_acc["nik"]
                nama_val = sel_acc["nama"]

        input_nik = st.text_input("Nomor Induk Kependudukan (NIK):", value=nik_val, placeholder="Ketik NIK 16 digit...")
        input_nama = st.text_input("Nama Penumpang:", value=nama_val, placeholder="Ketik nama penumpang...")

        # Validasi otomatis status biometrik wajah
        has_face = False
        passenger_db_info = None

        if input_nik:
            passenger_db_info = db.get_passenger(input_nik)
            has_face = db.has_face_template(input_nik)

            if passenger_db_info and has_face:
                st.markdown(f"""
                <div class="account-badge">
                    <strong>✅ Profil Biometrik Wajah Ditemukan!</strong><br>
                    Akun atas nama <strong>{passenger_db_info['nama']}</strong> telah memiliki data wajah terdaftar.<br>
                    <span style="font-size:12px; color:#1565C0;">Saat tiba di stasiun nanti, Anda bisa langsung masuk melalui Face Recognition Boarding Gate tanpa tiket fisik!</span>
                </div>
                """, unsafe_allow_html=True)
                
                # Tampilkan foto terdaftar jika ada
                if os.path.exists(passenger_db_info.get("foto_path", "")):
                    st.image(passenger_db_info["foto_path"], caption=f"Foto Wajah Terdaftar ({passenger_db_info['nama']})", width=140)
            elif passenger_db_info and not has_face:
                st.warning("⚠️ Akun ditemukan, namun belum merekam wajah. Silakan ke Menu 1 untuk merekam wajah agar bisa menggunakan Face Recognition Gate.")
            else:
                st.info("ℹ️ NIK baru: Akun akan otomatis dibuat. Namun agar dapat menggunakan Face Recognition Gate, pastikan mendaftarkan wajah di Menu 1.")

    with col_book_right:
        st.markdown("##### **2. Detail Perjalanan Kereta Api**")
        
        k_col1, k_col2 = st.columns(2)
        with k_col1:
            nama_kereta = st.selectbox(
                "Pilihan Kereta Api:",
                [
                    "Argo Parahyangan (KA 35)",
                    "Taksaka (KA 68)",
                    "Argo Bromo Anggrek (KA 2)",
                    "Lodaya (KA 92)",
                    "Gajayana (KA 55)",
                    "Turangga (KA 65)",
                    "Sembrani (KA 63)"
                ]
            )
            kelas_kereta = st.selectbox("Kelas Kereta:", ["Eksekutif", "Luxury Sleeper", "Bisnis", "Ekonomi Premium"])

        with k_col2:
            relasi_stasiun = st.selectbox(
                "Rute Perjalanan (Relasi):",
                [
                    "Gambir (GMR) - Bandung (BD)",
                    "Gambir (GMR) - Yogyakarta (YK)",
                    "Gambir (GMR) - Surabaya Pasarturi (SBI)",
                    "Bandung (BD) - Solo Balapan (SLO)",
                    "Gambir (GMR) - Malang (ML)",
                    "Surabaya Gubeng (SGU) - Bandung (BD)"
                ]
            )
            nomor_kursi = st.selectbox(
                "Gerbong & Nomor Kursi:",
                [
                    "Eksekutif 1 / 4A",
                    "Eksekutif 1 / 4B",
                    "Eksekutif 2 / 12A",
                    "Eksekutif 2 / 12D",
                    "Eksekutif 3 / 8B",
                    "Luxury 1 / 2A",
                    "Luxury 1 / 3B"
                ]
            )

        tgl_berangkat = st.date_input("Tanggal Keberangkatan:", value=date.today())
        jam_berangkat = st.time_input("Jam Keberangkatan:", value=time(8, 30))
        jadwal_str = f"{tgl_berangkat} {jam_berangkat}"

        # Generate Kode Booking unik PNR
        generated_code = "KAI-" + str(np.random.randint(100000, 999999))

        if st.button("💳 Konfirmasi & Terbitkan Tiket Kereta", type="primary", use_container_width=True):
            if not input_nik or not input_nama:
                st.error("Mohon isi NIK dan Nama Penumpang terlebih dahulu!")
            else:
                # Jika NIK belum ada di tabel penumpang, simpan dasar dulu
                if not passenger_db_info:
                    db.save_passenger(input_nik, input_nama, "Laki-laki", "081200000000", "")

                # Simpan tiket aktif
                db.save_ticket(
                    ticket_code=generated_code,
                    nik=input_nik,
                    nama_kereta=nama_kereta,
                    relasi=relasi_stasiun,
                    jadwal_berangkat=jadwal_str,
                    gerbong_kursi=f"{kelas_kereta} - {nomor_kursi}",
                    status_tiket="ACTIVE"
                )

                st.success(f"🎉 Tiket Kereta Berhasil Diterbitkan! Kode Booking: **{generated_code}**")
                st.markdown(f"""
                <div class="ticket-card">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <span style="font-weight:bold; color:#1E2B58; font-size:18px;">{nama_kereta}</span>
                        <span style="background:#ED6B23; color:white; padding:3px 10px; border-radius:5px; font-weight:bold;">{generated_code}</span>
                    </div>
                    <hr style="margin:10px 0;">
                    <p style="margin:4px 0;"><strong>Nama Penumpang:</strong> {input_nama}</p>
                    <p style="margin:4px 0;"><strong>NIK:</strong> {input_nik}</p>
                    <p style="margin:4px 0;"><strong>Rute:</strong> {relasi_stasiun}</p>
                    <p style="margin:4px 0;"><strong>Jadwal:</strong> {jadwal_str}</p>
                    <p style="margin:4px 0;"><strong>Kursi:</strong> <span style="color:#0077B6; font-weight:bold;">{nomor_kursi}</span></p>
                    <p style="margin:4px 0;"><strong>Status Tiket:</strong> <span style="color:green; font-weight:bold;">ACTIVE (Siap Digunakan di Boarding Gate)</span></p>
                </div>
                """, unsafe_allow_html=True)

# =========================================================
# MENU 3: SIMULASI BOARDING GATE (PINTU MASUK PERON KAI)
# =========================================================
elif menu == "3. 🚄 Simulasi Boarding Gate":
    st.subheader("🚄 Langkah 3: Pemindaian Wajah di Pintu Masuk Peron (Boarding Gate)")
    st.markdown("""
    Penumpang cukup berdiri dan menatap kamera di pintu masuk peron. 
    Sistem akan mengenali wajah menggunakan algoritma **LBPH**, lalu otomatis mencari tiket aktif milik penumpang tersebut.
    """)

    col_input, col_result = st.columns([1.1, 1.2])

    with col_input:
        input_mode = st.radio(
            "Pilih Sumber Masukan Citra Gate:",
            ["Pilih Foto Penumpang Terdaftar", "Kamera Langsung (Webcam)", "Unggah Foto Manual"],
            horizontal=True
        )

        test_image_bgr = None

        if input_mode == "Pilih Foto Penumpang Terdaftar":
            sample_files = [f for f in os.listdir(SAMPLE_FACES_DIR) if f.endswith(".jpg")]
            selected_file = st.selectbox(
                "Pilih Profil Penumpang / Orang Asing untuk Diuji:",
                sample_files,
                format_func=lambda x: "👤 " + x.replace(".jpg", "").replace("_", " ").title()
            )
            if selected_file:
                img_path = os.path.join(SAMPLE_FACES_DIR, selected_file)
                test_image_bgr = cv2.imread(img_path)
                st.image(cv2.cvtColor(test_image_bgr, cv2.COLOR_BGR2RGB), caption=f"Foto Masukan: {selected_file}", width=260)

        elif input_mode == "Kamera Langsung (Webcam)":
            camera_img = st.camera_input("Arahkan wajah Anda ke sensor kamera gate:")
            if camera_img is not None:
                file_bytes = np.asarray(bytearray(camera_img.read()), dtype=np.uint8)
                test_image_bgr = cv2.imdecode(file_bytes, 1)

        elif input_mode == "Unggah Foto Manual":
            uploaded_file = st.file_uploader("Unggah Foto Wajah (JPG / PNG):", type=["jpg", "jpeg", "png"])
            if uploaded_file is not None:
                file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
                test_image_bgr = cv2.imdecode(file_bytes, 1)
                st.image(cv2.cvtColor(test_image_bgr, cv2.COLOR_BGR2RGB), caption="Citra Diunggah", width=260)

    with col_result:
        st.markdown("#### **Status Verifikasi Boarding Gate**")

        if test_image_bgr is not None:
            # Jalankan Mesin Boarding KAI
            res = engine.process_frame(test_image_bgr, gate_id=selected_gate)

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

            # Tampilkan Frame Sensor Teranotasi
            st.image(
                cv2.cvtColor(res["annotated_frame"], cv2.COLOR_BGR2RGB),
                caption=f"Tampilan Sensor Kamera ({selected_gate})",
                use_container_width=True
            )

            # Metrik Komputasi
            m = res["metrics"]
            m_col1, m_col2, m_col3 = st.columns(3)
            m_col1.metric("Waktu Pemrosesan", f"{m['latency_ms']:.1f} ms")
            m_col2.metric("Distance Score (Chi-Square)", f"{m['distance']:.4f}")
            m_col3.metric("Kecocokan (Confidence)", f"{m['confidence']:.1f}%")

            # Tiket Penumpang Terverifikasi
            ticket = res.get("ticket")
            passenger = res.get("passenger")
            if passenger and ticket:
                st.markdown("---")
                st.markdown("#### 🎫 **Boarding Pass Elektronik (E-Ticket Terverifikasi Wajah)**")
                st.markdown(f"""
                <div class="ticket-card">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <span style="font-weight:bold; color:#1E2B58; font-size:18px;">{ticket['nama_kereta']}</span>
                        <span style="background:#ED6B23; color:white; padding:3px 10px; border-radius:5px; font-weight:bold;">{ticket['ticket_code']}</span>
                    </div>
                    <hr style="margin:10px 0;">
                    <p style="margin:4px 0;"><strong>Nama Penumpang:</strong> {passenger['nama']}</p>
                    <p style="margin:4px 0;"><strong>NIK:</strong> {passenger['nik']}</p>
                    <p style="margin:4px 0;"><strong>Relasi Stasiun:</strong> {ticket['relasi']}</p>
                    <p style="margin:4px 0;"><strong>Jadwal Keberangkatan:</strong> {ticket['jadwal_berangkat']}</p>
                    <p style="margin:4px 0;"><strong>Nomor Kursi:</strong> <span style="font-size:16px; color:#0077B6; font-weight:bold;">{ticket['gerbong_kursi']}</span></p>
                    <p style="margin:4px 0;"><strong>Waktu Masuk Gate:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                    <p style="margin:4px 0;"><strong>Status Tiket:</strong> <span style="color:green; font-weight:bold;">BOARDED (SUDAH DIGUNAKAN)</span></p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Pilih profil sampel di sebelah kiri atau arahkan webcam Anda untuk menyimulasikan pemindaian di boarding gate.")

# =========================================================
# MENU 4: PIPELINE PENGOLAHAN CITRA DIGITAL
# =========================================================
elif menu == "4. 🔬 Pipeline Pengolahan Citra":
    st.subheader("🔬 Visualisasi Mendalam Pipeline Pengolahan Citra Digital")
    st.markdown("""
    Halaman ini mendemonstrasikan secara visual transformasi citra tahap demi tahap 
    dari masukan kamera mentah hingga ekstraksi ciri tekstur **LBPH (Local Binary Pattern Histogram)**.
    """)

    sample_files = [f for f in os.listdir(SAMPLE_FACES_DIR) if f.endswith(".jpg")]
    sel_img_name = st.selectbox("Pilih Citra Subjek untuk Dianalisis:", sample_files)
    
    if sel_img_name:
        img_bgr = cv2.imread(os.path.join(SAMPLE_FACES_DIR, sel_img_name))
        stages = preprocessor.get_intermediate_stages(img_bgr)
        norm_face = stages["6. Normalisasi Ukuran (128x128)"]
        lbp_map = extractor.compute_lbp_image(norm_face)
        stages["7. Peta Tekstur Spasial (LBP 2D)"] = lbp_map

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
            "4. Metrik Jarak Chi-Square"
        ])

        with tab_gray:
            st.markdown(r"""
            #### Konversi Grayscale & Filter Bilateral
            - **Grayscale (ITU-R BT.601)**:
              $$I_{\text{gray}} = 0.299 \cdot R + 0.587 \cdot G + 0.114 \cdot B$$
              Mereduksi dimensi ruang warna dari 3 kanal RGB menjadi 1 kanal luminansi tanpa kehilangan informasi tepi.
            - **Bilateral Filtering**:
              $$I^{\text{filtered}}(x) = \frac{1}{W_p} \sum_{x_i \in \Omega} I(x_i) f_r(\|I(x_i) - I(x)\|) g_s(\|x_i - x\|)$$
              Menghaluskan derau sensor seragam namun **mempertahankan ketajaman tepi kontur mata, bibir, dan hidung**.
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
            - Jika $D_{\chi^2} < \text{Threshold}$ (default = 0.22): **Wajah Cocok (Genuine Passenger)**.
            - Jika $D_{\chi^2} \ge \text{Threshold}$: **Wajah Berbeda (Impostor / Ditolak)**.
            """)

# =========================================================
# MENU 5: EVALUASI & METRIK SISTEM
# =========================================================
elif menu == "5. 📊 Evaluasi & Metrik Sistem":
    st.subheader("📊 Evaluasi Kinerja dan Analisis Kuantitatif Sistem")
    st.markdown("""
    Modul evaluasi ini menguji performa sistem berdasarkan ketentuan pengujian resmi Bagian 9 dokumen tugas:
    - **Metrik Klasifikasi Biometrik**: Accuracy, Precision, Recall, F1-Score, False Acceptance Rate (FAR), dan False Rejection Rate (FRR).
    - **Ketahanan Lingkungan**: Evaluasi pada kondisi normal, redup (dim), silau (bright), derau sensor, dan rotasi sudut kepala.
    """)

    if st.button("🚀 Jalankan Pengujian Otomatis (Benchmark Suite)", type="primary"):
        with st.spinner("Menjalankan benchmark biometrik komprehensif pada foto manusia asli..."):
            samples = {}
            for f in os.listdir(SAMPLE_FACES_DIR):
                if f.endswith(".jpg") and not f.startswith("impostor"):
                    p_name = f.replace(".jpg", "")
                    samples[p_name] = cv2.imread(os.path.join(SAMPLE_FACES_DIR, f))

            res = evaluator.run_benchmark_suite(samples, threshold=current_threshold)
            st.session_state["benchmark_results"] = res
            st.success("Pengujian benchmark selesai!")

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

# =========================================================
# MENU 6: DATA MANIFEST & AUDIT LOG GATE
# =========================================================
elif menu == "6. 📋 Data Manifest & Audit Log":
    st.subheader("📋 Data Akun Penumpang, Tiket Kereta, dan Audit Log Gerbang")

    tab_accounts, tab_tickets, tab_logs = st.tabs([
        "1. Akun Penumpang & Wajah Terdaftar",
        "2. Manifest Seluruh Tiket Kereta",
        "3. Catatan Audit Log Boarding Gate"
    ])

    with tab_accounts:
        passengers = db.get_all_passengers()
        if passengers:
            df_acc = pd.DataFrame(passengers)
            st.dataframe(df_acc, use_container_width=True)
        else:
            st.info("Belum ada akun penumpang yang terdaftar.")

    with tab_tickets:
        with db._get_connection() as conn:
            all_tickets = conn.execute("""
                SELECT t.ticket_code, p.nama, t.nik, t.nama_kereta, t.relasi, 
                       t.jadwal_berangkat, t.gerbong_kursi, t.status_tiket, t.waktu_boarding
                FROM tickets t
                JOIN passengers p ON t.nik = p.nik
                ORDER BY t.jadwal_berangkat DESC
            """).fetchall()
            if all_tickets:
                df_t = pd.DataFrame([dict(r) for r in all_tickets])
                st.dataframe(df_t, use_container_width=True)
            else:
                st.info("Belum ada tiket kereta yang dipesan.")

    with tab_logs:
        logs = db.get_recent_logs(limit=100)
        if logs:
            df_logs = pd.DataFrame(logs)
            st.dataframe(df_logs, use_container_width=True)
        else:
            st.info("Belum ada transaksi boarding yang tercatat.")
