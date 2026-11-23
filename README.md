# 🚄 Smart Boarding Gate KAI - Face Recognition System
### Tugas Proyek Akhir Mata Kuliah Pengolahan Citra Digital (Semester 5)
Program Studi S1 Teknik Informatika — Tahun Akademik 2026/2027

---

![KAI Face Recognition Boarding Gate](https://upload.wikimedia.org/wikipedia/commons/5/56/Logo_PT_Kereta_Api_Indonesia_%28Persero%29_2020.svg)

## 📌 Ringkasan Proyek
Proyek ini mengimplementasikan sistem gerbang peron otomatis berbasis biometrik pengenalan wajah (*Face Recognition Boarding Gate*) yang meniru fasilitas resmi PT Kereta Api Indonesia (Persero). Sistem ini memanfaatkan prinsip-prinsip komputasi **Pengolahan Citra Digital (Digital Image Processing)** untuk mengidentifikasi penumpang secara nirsentuh (*contactless*) dan memvalidasi keabsahan tiket perjalanan kereta api secara *real-time*.

### 🔬 Komponen Pengolahan Citra Digital:
1. **Deteksi Wajah (ROI):** Viola-Jones Haar Cascade Classifier & Segmentasi Ruang Warna Kulit YCrCb adaptif.
2. **Prapemrosesan Citra:** 
   - Grayscale conversion (ITU-R BT.601)
   - Bilateral Filtering (peredaman derau dengan preservasi tepi)
   - CLAHE (*Contrast Limited Adaptive Histogram Equalization*) untuk mengatasi variasi pencahayaan ekstrem stasiun kereta
   - Normalisasi geometri bikubik ($128 \times 128$ piksel)
3. **Ekstraksi Ciri Tekstur Spasial:** *Local Binary Pattern Histogram* (LBPH) berpartisi $8 \times 8$ sel ($16.384$ dimensi fitur spasial).
4. **Pencocokan Biometrik 1:N:** Jarak statistik *Chi-Square Distance* ($\chi^2$).
5. **Logika Bisnis Kereta Api:** Pengecekan status manifest tiket (`ACTIVE`, `BOARDED`, `NO_TICKET`) dan pencegahan *double-entry* (*anti pass-back*).

---

## 📂 Struktur Direktori Proyek

```text
Pengolahan Citra/
├── app.py                      # Aplikasi Web Interaktif Streamlit (KAI Smart Gate GUI)
├── main_cli.py                 # Skrip Uji Cepat Mode Baris Perintah (CLI)
├── test_system.py              # Suite Pengujian Otomatis (Unit Test Integrasi 100% Pass)
├── requirements.txt            # Daftar pustaka dependensi Python
├── README.md                   # Dokumentasi umum proyek
│
├── src/                        # Modul Inti Pengolahan Citra & Bisnis
│   ├── __init__.py
│   ├── config.py               # Konfigurasi parameter ambang batas & direktori
│   ├── detector.py             # Detektor wajah hybrid (Haar Cascade & YCrCb)
│   ├── preprocessing.py        # Modul prapemrosesan (Grayscale, Bilateral, CLAHE, Resize)
│   ├── feature_extractor.py    # Ekstraktor ciri LBPH dan PCA Eigenfaces murni
│   ├── database.py             # Pengelola SQLite (penumpang, template wajah, tiket, audit log)
│   ├── boarding_engine.py      # Mesin utama simulasi gate & aturan bisnis KAI
│   ├── evaluator.py            # Modul benchmark kuantitatif & pembuat grafik analitis
│   └── seed_data.py            # Inisialisasi basis data manifest & citra sampel wajah
│
├── data/
│   ├── kai_boarding.db         # Basis data relasional SQLite
│   ├── sample_faces/           # Citra wajah sampel penumpang & impostor
│   └── evaluation_results/     # Grafik analitis (Confusion Matrix, ROC, FAR-FRR, Latensi)
│
└── docs/                       # Dokumen Luaran Wajib Tugas Akhir
    ├── LAPORAN_PROYEK_AKHIR.md # Laporan lengkap sesuai struktur BAB I s/d BAB V (Bagian 7)
    ├── ARTIKEL_ILMIAH.md       # Draf artikel ilmiah format publikasi IEEE (Bagian 8)
    └── PANDUAN_PRESENTASI.md   # Panduan pembagian bicara & skenario live demo Pertemuan 14-15
```

---

## ⚡ Panduan Instalasi & Penggunaan

### 1. Prasyarat Lingkungan
Pastikan komputer Anda telah terpasang:
- Python 3.10 atau versi lebih baru (diuji stabil pada Python 3.13.12 x64)
- Git (opsional)

### 2. Instalasi Dependensi
Buka terminal (PowerShell atau Command Prompt) pada direktori proyek, lalu jalankan:
```bash
pip install -r requirements.txt
```

### 3. Inisialisasi Basis Data & Citra Sampel
Jalankan skrip *seeder* untuk mengisi manifest penumpang dan template biometrik awal:
```bash
python -m src.seed_data
```

### 4. Menjalankan Unit Test Otomatis
Validasi seluruh fungsionalitas sistem dengan unit test:
```bash
python test_system.py
```
*Hasil yang diharapkan: `SEMUA PENGUJIAN INTEGRASI PIPELINE BERHASIL 100%!`*

### 5. Menjalankan Aplikasi Web Interaktif (Streamlit)
Untuk membuka antarmuka visual bergaya *Smart Gate* KAI:
```bash
streamlit run app.py
```
Aplikasi akan otomatis terbuka pada peramban web Anda di alamat: `http://localhost:8501`.

---

## 📊 Hasil Pengujian & Evaluasi Kinerja (Bagian 9)

Berdasarkan pengujian biometrik 50 sampel validasi sesuai protokol standar NIST pada ambang batas optimal $\theta = 0,28$:

| Metrik Evaluasi | Nilai Kinerja |
| :--- | :---: |
| **Akurasi (Overall Accuracy)** | **98,00%** |
| **Presisi (Precision)** | **96,15%** |
| **Recall / Sensitivitas** | **100,00%** |
| **F1-Score** | **98,04%** |
| **False Acceptance Rate (FAR)** | **4,00%** |
| **False Rejection Rate (FRR)** | **0,00%** |
| **Total Waktu Pemrosesan per Frame** | **34,9 ms (~28,6 FPS)** |

Grafik evaluasi resolusi tinggi tersimpan pada folder `data/evaluation_results/`:
- `confusion_matrix.png`: Matriks kebingungan klasifikasi biometrik
- `condition_robustness.png`: Ketahanan sistem terhadap 5 kondisi stasiun (normal, redup, silau, noise, tilt)
- `far_frr_curve.png`: Kurva *trade-off* FAR vs FRR dan titik potong EER
- `latency_breakdown.png`: Rincian waktu eksekusi masing-masing tahapan pemrosesan
- `pipeline_stages.png`: Visualisasi tahapan citra dari BGR hingga peta tekstur 2D LBP

---

## 👥 Tim Pengembang (Kelompok 4 - Kelas PCD-A)
1. **Muhammad Fadhil Pratama** (NIM: 10122001) - *Project Lead & System Architect*
2. **Nabila Putri Ramadhani** (NIM: 10122015) - *Image Preprocessing Specialist*
3. **Bagus Aryo Wicaksono** (NIM: 10122028) - *Feature Extraction & Metric Engineer*
4. **Jessica Aurelia Tan** (NIM: 10122042) - *UI/UX & Database Developer*
5. **Rizky Dwi Kurniawan** (NIM: 10122057) - *QA, Benchmarking & Technical Writer*
