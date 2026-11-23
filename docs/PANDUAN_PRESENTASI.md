# PANDUAN PRESENTASI & DEMO APLIKASI
### TUGAS PROYEK AKHIR PENGOLAHAN CITRA DIGITAL (PERTEMUAN 14-15)

---

## 🎯 TOPIK: SMART BOARDING GATE KAI BERBASIS FACE RECOGNITION (CLAHE & LBPH)

Panduan ini disusun khusus untuk mempersiapkan demonstrasi langsung (*live demo*) dan presentasi kelompok di hadapan dosen penguji pada Pertemuan 14-15 sesuai ketentuan silabus perkuliahan.

---

## 👥 1. PEMBAGIAN PERAN & GILIRAN BICARA (DURASI TOTAL: 15 MENIT)

| No. | Nama Mahasiswa | Peran | Durasi | Materi yang Dipresentasikan |
| :---: | :--- | :--- | :---: | :--- |
| 1. | **Muhammad Fadhil Pratama** (Ketua) | *Opening & Problem Statement* | 2.5 Menit | Pembukaan, latar belakang masalah antrean stasiun KAI, tujuan proyek, dan ikhtisar arsitektur sistem *smart gate*. |
| 2. | **Nabila Putri Ramadhani** | *Image Preprocessing Specialist* | 3.0 Menit | Penjelasan teoritis & matematis: Grayscale ITU-R BT.601, Filter Bilateral (anti-derau), dan CLAHE (normalisasi pencahayaan ubin $8 \times 8$). |
| 3. | **Bagus Aryo Wicaksono** | *Feature Extraction & Metric* | 3.0 Menit | Penjelasan ekstraksi tekstur spasial LBPH ($8 \times 8$ sel, $16.384$ dimensi), perbandingan jarak statistik $\chi^2$ (*Chi-Square*), dan *thresholding*. |
| 4. | **Jessica Aurelia Tan** | *Live Demo Operator* | 4.0 Menit | Mendemonstrasikan 5 skenario nyata pada aplikasi Streamlit: penumpang sah, *anti double-entry*, tanpa tiket, penyusup, dan registrasi baru. |
| 5. | **Rizky Dwi Kurniawan** | *Evaluation & Closing* | 2.5 Menit | Pembahasan grafik evaluasi kuantitatif (Confusion Matrix, kurva FAR-FRR, uji ketahanan stasiun, latensi 34,9 ms / 28,6 FPS), dan kesimpulan. |

---

## 🖥️ 2. SKENARIO DEMONSTRASI APLIKASI LIVE (STREAMLIT)

### Persiapan Sebelum Demo:
1. Buka terminal di direktori proyek:
   ```powershell
   cd "d:\.KULIAH\Semester 5\Pengolahan Citra"
   streamlit run app.py
   ```
2. Aplikasi akan terbuka di `http://localhost:8501`. Pastikan proyektor menampilkan layar penuh (*Full Screen* / F11).

### Urutan Eksekusi Demo di Depan Dosen:

#### **Skenario A: Penumpang Sah dengan Tiket Aktif (Akses Diterima)**
1. Masuk ke tab menu **"🚄 Simulasi Boarding Gate"**.
2. Pilih input: **"Pilih Sampel Penumpang KAI"** $\to$ Pilih `3273011204980001_budi_santoso.jpg`.
3. Tunjukkan ke dosen:
   - Banner status hijau: **`✅ PINTU TERBUKA (GATE OPEN)`**.
   - Bounding box beranotasi modern dengan nama subjek (*HUD Corner Brackets*).
   - Tiket elektronik (*E-Boarding Pass*) otomatis terbit (KA Argo Parahyangan, Eksekutif 2 / 12A).
   - Metrik komputasi: Latensi $\approx 30-35$ ms, Jarak $\approx 0,21$ ($< 0,245$), Confidence $\approx 40-50\%$.

#### **Skenario B: Pencegahan Akses Ganda / Anti Pass-Back (Tiket Sudah Dipakai)**
1. Pada orang yang sama (`Budi Santoso`), tekan tombol refresh atau pilih kembali fotonya.
2. Tunjukkan ke dosen:
   - Banner status merah: **`⛔ PINTU TERKUNCI (ACCESS DENIED)`**.
   - Pesan sistem: *"Tiket KAI-7G4B9X atas nama Budi Santoso sudah digunakan pada [Timestamp]"*.
   - **Poin Nilai Tambah Akademik:** Jelaskan bahwa sistem tidak hanya mengenali wajah, namun memiliki integritas aturan bisnis perkeretaapian untuk mencegah penumpang menyelinap ganda menggunakan tiket yang sama!

#### **Skenario C: Penumpang Terdaftar Namun Tidak Memiliki Tiket (Akses Ditolak)**
1. Pilih subjek: `3271032805970005_rian_kurniawan.jpg`.
2. Hasil: Wajah terverifikasi sebagai Rian Kurniawan, namun pintu tetap terkunci dengan status **`TIKET TIDAK DITEMUKAN`**.

#### **Skenario D: Orang Asing / Impostor (Penyusup Ditolak)**
1. Pilih subjek: `impostor_unregistered.jpg`.
2. Hasil: Pintu gerbang merah terkunci dengan status **`TIDAK TERDAFTAR (UNRECOGNIZED)`** karena jarak $\chi^2$ melebihi ambang batas ($> 0,245$).

#### **Skenario E: Pamerkan Visualisasi Pipeline Pengolahan Citra (Tab 2)**
1. Buka tab **"🔬 Pipeline Pengolahan Citra"**.
2. Tunjukkan kepada dosen 7 tahapan matriks visual:
   `Citra Asli` $\to$ `Grayscale` $\to$ `Bilateral Filter` $\to$ `Ekualisasi Global` $\to$ `CLAHE Adaptif` $\to$ `Normalisasi 128x128` $\to$ `Peta Tekstur LBP 2D`.
3. Tunjukkan tab rumus matematis di bawahnya jika dosen meminta pembuktian persamaan.

#### **Skenario F: Dasbor Metrik Akademik (Tab 4)**
1. Buka tab **"📊 Evaluasi & Metrik Sistem"**.
2. Tunjukkan grafik yang telah dihasilkan:
   - *Confusion Matrix*: Akurasi **98,00%**, Presisi **96,15%**, Recall **100,00%**, F1 **98,04%**.
   - Kurva FAR vs FRR: Titik potong EER pada ambang batas optimal.
   - Grafik ketahanan kondisi stasiun: 100% pada normal, redup, silau, noise, dan kemiringan kepala.
   - Grafik perincian latensi (Total pemrosesan 34,9 ms atau ~28,6 FPS).

---

## ❓ 3. ANTISIPASI PERTANYAAN KRITIS DOSEN & JAWABAN TEPAT

### Q1: *"Mengapa memilih metode klasik CLAHE + LBPH daripada langsung menggunakan Deep Learning (CNN/ResNet)?"*
> **Jawaban:**  
> *"Izin menjawab Bapak/Ibu Dosen. Terdapat tiga alasan fundamental:  
> 1. **Kesesuaian Silabus Pengolahan Citra Digital:** Metode CLAHE dan LBPH secara langsung menerapkan prinsip fundamental pengolahan citra piksel, ekualisasi histogram lokal, konvolusi non-linier, dan perbandingan distribusi statistik $\chi^2$ yang transparan secara matematis tanpa bersifat 'black box'.  
> 2. **Efisiensi Komputasi Hardware Edge:** Gerbang stasiun (*turnstile gate*) mengandalkan unit komputasi tertanam (*embedded industrial PC*). Metode LBPH kami hanya membutuhkan waktu 34,9 ms pada CPU biasa tanpa GPU bernilai puluhan juta rupiah.  
> 3. **Kebutuhan Data Enrolment:** Deep Learning membutuhkan ribuan citra per orang untuk pelatihan ulang, sedangkan LBPH dengan CLAHE bekerja optimal menggunakan konsep *One-Shot Biometric Matching* (cukup 1 foto KTP saat registrasi)."*

### Q2: *"Bagaimana CLAHE bekerja mengatasi silau lampu stasiun dibanding ekualisasi biasa?"*
> **Jawaban:**  
> *"Ekualisasi histogram standar mendistribusikan probabilitas kumulatif (CDF) secara global pada seluruh citra, yang justru menyebabkan area terang tersaturasi penuh menjadi putih (kliping piksel 255) dan memperbesar noise latar belakang. CLAHE membagi citra ke dalam ubin lokal $8 \times 8$ dan menerapkan pemotongan kontras (*clip limit* 2.5). Piksel yang melebihi batas dipotong dan disebar merata ke bin lain sebelum ekualisasi, diikuti interpolasi bilinear sehingga iluminasi stabil di seluruh permukaan wajah."*

### Q3: *"Mengapa menggunakan jarak Chi-Square ($\chi^2$), bukan Euclidean atau Manhattan?"*
> **Jawaban:**  
> *"Karena fitur LBPH adalah histogram frekuensi diskret. Jarak Chi-Square memberikan bobot komparasi berbasis distribusi proporsional dengan formula $(H_1 - H_2)^2 / (H_1 + H_2)$, di mana perbedaan pada bin dengan frekuensi rendah tidak mendominasi perhitungan secara tidak adil seperti yang terjadi pada Euclidean norm ($L_2$)."*

---

## 📋 4. CHECKLIST HARI-H DEMO
- [x] Laptop terhubung ke adaptor daya (mencegah *throttling* CPU).
- [x] Database telah di-seed dengan sampel lengkap (`python -m src.seed_data`).
- [x] Web server Streamlit aktif dan dapat diakses di browser (`streamlit run app.py`).
- [x] Berkas `requirements.txt` dan unit test `python test_system.py` dipastikan bernilai 100% lolos.
- [x] Draf laporan proyek dan artikel ilmiah telah dicetak/disiapkan dalam format PDF/Markdown.
