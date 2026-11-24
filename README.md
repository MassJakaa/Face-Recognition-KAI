# 🚄 KAI Smart Boarding Gate - Face Recognition System
### Tugas Proyek Akhir Mata Kuliah Pengolahan Citra Digital
**Program Studi S1 Informatika — Kelas Pengolahan Citra IF-B**

---

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)
![OpenCV](https://img.shields.io/badge/OpenCV-5.0%20%2F%204.10-green?logo=opencv)
![Streamlit](https://img.shields.io/badge/Streamlit-1.57-red?logo=streamlit)
![License](https://img.shields.io/badge/License-MIT-yellow)
![Status](https://img.shields.io/badge/Build-Passing-brightgreen)

---

## 📌 Ringkasan Proyek
Proyek ini mengimplementasikan purwarupa sistem gerbang peron otomatis berbasis biometrik pengenalan wajah (*Face Recognition Boarding Gate*) yang meniru fasilitas operasional resmi **PT Kereta Api Indonesia (Persero)**. Sistem dirancang untuk menggantikan pemeriksaan tiket fisik konvensional secara nirsentuh (*contactless*) dengan mengintegrasikan alur penuh: **Pendaftaran Akun Biometrik Wajah**, **Pemesanan Tiket (cukup NIK & Nama)**, dan **Verifikasi Masuk Peron Otomatis**.

Sistem menerapkan prinsip-prinsip fundamental **Pengolahan Citra Digital (Digital Image Processing / DIP)**:
1. **Deteksi Wajah & Penyejajaran Sudut (*Eye Alignment*):** Isolasi ROI wajah dengan Viola-Jones Haar Cascade serta rotasi afin otomatis berbasis deteksi sepasang mata agar garis mata sejajar horizontal.
2. **Prapemrosesan Citra Digital:**
   - Konversi ruang warna Grayscale luminansi (ITU-R BT.601)
   - Reduksi derau adaptif menggunakan *Bilateral Filter* (menghaluskan tekstur kulit tanpa mengaburkan tepi kontur mata/bibir)
   - Peningkatan kontras adaptif lokal dengan **CLAHE** (*Contrast Limited Adaptive Histogram Equalization*) untuk mengatasi fluktuasi pencahayaan ekstrem stasiun (silau matahari, lampu sorot, atau bayangan malam hari)
   - Normalisasi geometri bikubik ($128 \times 128$ piksel)
3. **Ekstraksi Ciri Tekstur Mikro (LBPH):** Operator *Local Binary Pattern* dengan partisi $8 \times 8$ sel lokal, menghasilkan vektor ciri spasial berdimensi **16.384 fitur**.
4. **Pencocokan Biometrik 1:N:** Menggunakan metrik jarak statistik **Chi-Square Distance ($\chi^2$)**.
5. **Logika Bisnis Kereta Api:** Validasi status tiket (`ACTIVE`, `BOARDED`, `WRONG_DATE`, `NO_TICKET`) dan pencegahan akses ganda (*anti pass-back* / *double entry*).

---

## 🔄 Alur Kerja Sistem (Workflow KAI)

```
[Langkah 1: Kios/App KAI]           [Langkah 2: Pemesanan Tiket]           [Langkah 3: Di Stasiun]
Registrasi Akun + Rekam Muka   ➔    Pesan Tiket (Cukup NIK & Nama)    ➔    Masuk Peron (Scan Wajah)
(Dilakukan SEKALI di awal)         (Otomatis pakai wajah Langkah 1)       (Pintu Gate Terbuka Otomatis)
```

1. **Langkah 1: Registrasi Akun & Wajah (Enrolment)**
   Penumpang mendaftar akun satu kali dengan memasukkan data identitas e-KTP (NIK, Nama, Gender, No. HP) dan mengambil foto wajah via kamera/upload. Wajah dienkripsi ke dalam template biometrik LBPH. **Pada tahap ini belum ada pemesanan tiket.**
2. **Langkah 2: Pemesanan Tiket Kereta (Booking)**
   Penumpang cukup memasukkan NIK dan Nama (atau memilih dari akun terdaftar). Sistem otomatis memverifikasi profil wajah yang sudah ada. Penumpang memilih kereta, rute, tanggal, dan kursi. Tiket diterbitkan dengan status `ACTIVE` dan otomatis terhubung dengan wajah penumpang.
3. **Langkah 3: Simulasi Masuk Peron (Boarding Gate)**
   Penumpang berdiri di depan kamera gate tanpa perlu menunjukkan tiket fisik atau KTP. Sistem mencocokkan wajah $\rightarrow$ mengambil tiket aktif milik NIK tersebut $\rightarrow$ membuka pintu gerbang (**GATE OPEN**) dan mencatat audit log.

---

## 🚦 Status Respon Gerbang (Gate Responses)

| Status Gate | Respon Fisik | Keterangan |
| :--- | :---: | :--- |
| **`SUCCESS`** | 🟢 **Pintu Terbuka (Gate Open)** | Wajah cocok dan tiket berstatus `ACTIVE` untuk jadwal hari ini. Tiket otomatis diubah ke `BOARDED`. |
| **`ALREADY_BOARDED`** | 🔴 **Pintu Terkunci (Access Denied)** | Wajah cocok, namun tiket sudah pernah digunakan sebelumnya (*mencegah penyusupan tiket ganda / anti pass-back*). |
| **`WRONG_DATE`** | 🔴 **Pintu Terkunci (Access Denied)** | Wajah cocok dan tiket valid, namun jadwal keberangkatan tertera untuk tanggal yang berbeda dari hari ini. |
| **`NO_TICKET`** | 🔴 **Pintu Terkunci (Access Denied)** | Wajah dikenali sebagai akun terdaftar, namun tidak memiliki tiket perjalanan aktif di stasiun tersebut. |
| **`UNRECOGNIZED`** | 🔴 **Pintu Terkunci (Access Denied)** | Wajah tidak ditemukan di basis data biometrik (jarak Chi-Square $\ge$ ambang batas). |
| **`NO_FACE`** | 🟡 **Menunggu (Waiting)** | Tidak ada wajah yang terdeteksi di depan sensor kamera gate. |

---

## 📂 Struktur Direktori Repositori

```text
Face-Recognition-KAI/
├── app.py                      # Aplikasi Web Interaktif Streamlit (Smart Gate GUI)
├── main_cli.py                 # Skrip Uji Cepat Mode Terminal (CLI)
├── test_system.py              # Suite Pengujian Otomatis (Unit Test 100% Pass)
├── requirements.txt            # Daftar pustaka dependensi Python
├── README.md                   # Dokumentasi utama proyek
│
├── src/                        # Modul Inti Pengolahan Citra & Sistem
│   ├── __init__.py
│   ├── config.py               # Konfigurasi parameter ambang batas & direktori
│   ├── detector.py             # Detektor wajah hybrid, penyejajaran mata (eye alignment), & HUD
│   ├── preprocessing.py        # Modul prapemrosesan (Grayscale, Bilateral Filter, CLAHE, Resize)
│   ├── feature_extractor.py    # Ekstraksi tekstur LBPH (16.384 dimensi), Chi-Square, & PCA
│   ├── database.py             # Pengelola SQLite (penumpang, template biometrik, manifest tiket, log audit)
│   ├── boarding_engine.py      # Mesin utama simulasi boarding gate & validasi aturan tiket KAI
│   ├── evaluator.py            # Modul benchmark kuantitatif & pembangkit grafik analitis
│   └── seed_data.py            # Inisialisasi basis data manifest & dataset foto manusia asli
│
├── data/
│   ├── kai_boarding.db         # Basis data relasional SQLite
│   ├── haarcascade_frontalface_default.xml # Model deteksi wajah lokal
│   ├── haarcascade_eye.xml     # Model deteksi mata untuk penyejajaran sudut miring
│   ├── sample_faces/           # Foto wajah asli penumpang terdaftar & orang asing (impostor)
│   └── evaluation_results/     # Grafik analitis (Confusion Matrix, FAR-FRR, Ketahanan, Latensi)
│
└── docs/                       # Dokumen Luaran Akademik Wajib
    ├── LAPORAN_PROYEK_AKHIR.md # Laporan lengkap sesuai struktur BAB I s/d BAB V (Bagian 7)
    ├── ARTIKEL_ILMIAH.md       # Draf artikel ilmiah format publikasi IEEE (Bagian 8)
    └── PANDUAN_PRESENTASI.md   # Panduan pembagian bicara & skenario live demo Pertemuan 14-15
```

---

## ⚡ Panduan Instalasi & Penggunaan

### 1. Prasyarat Lingkungan
- Python versi 3.10 atau lebih baru (direkomendasikan Python 3.11 s/d 3.13 x64)
- Git

### 2. Kloning Repositori & Masuk ke Folder Proyek
```bash
git clone https://github.com/MassJakaa/Face-Recognition-KAI.git
cd Face-Recognition-KAI
```

### 3. Instalasi Dependensi
```bash
pip install -r requirements.txt
```

### 4. Menjalankan Aplikasi Web Interaktif (Streamlit)
Gunakan perintah berikut:
```bash
python -m streamlit run app.py
```
> [!TIP]
> Menggunakan awalan `python -m streamlit` memastikan aplikasi langsung berjalan stabil di Windows PowerShell tanpa kendala *environment variable PATH*.
> Peramban web akan otomatis terbuka di alamat: **`http://localhost:8501`**.

### 5. Menjalankan Pengujian Cepat Mode Terminal (CLI)
```bash
python main_cli.py
```

### 6. Menjalankan Unit Test Integrasi Sistem
```bash
python test_system.py
```
*(Memvalidasi database, deteksi wajah, filter CLAHE, ekstraksi LBPH, dan aturan boarding dengan hasil kelulusan 100%).*

---

## 📊 Hasil Pengujian & Evaluasi Kinerja (Bagian 9)

Pengujian biometrik dilakukan mengacu pada protokol evaluasi standar **NIST** terhadap 50 sampel validasi (*genuine* dan *impostor*) melintasi berbagai kondisi lingkungan stasiun (normal, redup $\gamma=1.25$, silau $\gamma=0.82$, derau sensor $\sigma=3.5$, dan rotasi pose kepala $\pm 2.5^\circ$):

| Metrik Evaluasi | Nilai Kinerja | Keterangan & Analisis |
| :--- | :---: | :--- |
| **Akurasi (Overall Accuracy)** | **98,00%** | Tingkat ketepatan klasifikasi total antara penumpang sah dan penyusup. |
| **Presisi (Precision)** | **96,15%** | Probabilitas bahwa subjek yang diizinkan masuk benar-benar penumpang sah. |
| **Recall / Sensitivitas** | **100,00%** | Tidak ada penumpang sah yang tertolak (FRR = 0,00%). |
| **F1-Score** | **98,04%** | Keseimbangan harmonik optimal antara presisi dan sensitivitas. |
| **False Acceptance Rate (FAR)** | **4,00%** | Tingkat kesalahan penyusup/impostor yang keliru diberikan akses. |
| **False Rejection Rate (FRR)** | **0,00%** | Tingkat penolakan keliru terhadap penumpang tiket aktif. |
| **Total Waktu Pemrosesan per Frame** | **34,9 ms** | Eksekusi sangat cepat pada CPU standar (**~28,6 FPS / Real-Time**). |

Grafik evaluasi resolusi tinggi tersimpan pada folder `data/evaluation_results/`:
- `confusion_matrix.png`: Matriks kebingungan klasifikasi biometrik
- `condition_robustness.png`: Ketahanan sistem terhadap 5 kondisi stasiun (normal, redup, silau, noise, tilt)
- `far_frr_curve.png`: Kurva *trade-off* FAR vs FRR dan titik potong EER
- `latency_breakdown.png`: Rincian waktu eksekusi masing-masing tahapan pemrosesan
- `pipeline_stages.png`: Visualisasi tahapan citra dari BGR hingga peta tekstur 2D LBP

---

## 👥 Tim Pengembang (Kelompok Pengolahan Citra IF-B)

| Nama Mahasiswa | NIM | Peran & Kontribusi Utama |
| :--- | :---: | :--- |
| **Rafi Dzaka Pratama Putra** | **123240104** | **Database, Aturan Bisnis Tiket, & Integrasi Sistem** |
| **Raihan Natawangsa** | **123240120** | **Antarmuka Grafis Streamlit & Visualisasi UI/UX** |
| **Ichsan Wahyu Priambudi** | **123240122** | **Deteksi Wajah, Prapemrosesan CLAHE, & Ekstraksi Ciri LBPH** |
| **Indra Naufal Firdaus** | **123240195** | **Penyusunan Dataset, Pengujian Kuantitatif, & Evaluasi Metrik** |

---

## 📄 Lisensi
Proyek ini dikembangkan untuk keperluan akademik Mata Kuliah Pengolahan Citra Digital, Program Studi Informatika, Tahun Akademik 2026/2027, dan dilisensikan di bawah lisensi MIT.
