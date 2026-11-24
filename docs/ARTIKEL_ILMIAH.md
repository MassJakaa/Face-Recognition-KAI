# DRAF ARTIKEL ILMIAH
### MATA KULIAH PENGOLAHAN CITRA DIGITAL (IF-3105)

---

# Optimasi Pengenalan Wajah Otomatis pada Smart Boarding Gate Stasiun Kereta Api Menggunakan CLAHE dan Local Binary Pattern Histogram (LBPH)

**Rafi Dzaka Pratama Putra$^{1,*}$, Raihan Natawangsa$^1$, Ichsan Wahyu Priambudi$^1$, Indra Naufal Firdaus$^1$**  
$^1$Program Studi S1 Informatika, Fakultas Teknologi Informasi  
$^*$Penulis Korespondensi: `rafidzaka5@gmail.com`

---

### ABSTRAK
Antrean pada pintu pemeriksaan tiket masuk peron stasiun kereta api menjadi salah satu titik kemacetan utama dalam operasional transportasi massal berkecepatan tinggi. Penerapan sistem biometrik *Face Recognition Boarding Gate* oleh PT Kereta Api Indonesia (Persero) bertujuan mengeliminasi pemeriksaan manual tiket fisik. Namun, fluktuasi pencahayaan stasiun (*glare*, bayangan tajam, dan pencahayaan temaram) serta kebutuhan verifikasi *real-time* menuntut algoritma pengolahan citra digital yang adaptif dan efisien. Penelitian ini mengusulkan arsitektur pengenalan wajah berbasis kombinasi penapis bilateral (*Bilateral Filter*), *Contrast Limited Adaptive Histogram Equalization* (CLAHE), deskriptor tekstur *Local Binary Pattern Histogram* (LBPH) berpartisi $8 \times 8$ sel, serta metrik jarak *Chi-Square* ($\chi^2$). Sistem diuji menggunakan 50 data validasi mengacu pada protokol standar biometrik NIST yang mencakup kondisi normal, redup ($\gamma = 1.25$), silau ($\gamma = 0.82$), derau sensor ($\sigma = 3.5$), serta kemiringan pose kepala ($\pm 2.5^\circ$). Hasil eksperimen membuktikan sistem mencapai akurasi sebesar 98,00%, presisi 96,15%, *recall* 100,00%, F1-*score* 98,04%, serta *False Acceptance Rate* (FAR) 4,00% pada nilai ambang batas $\theta = 0,22$. Rata-rata waktu latensi komputasi adalah 34,9 ms (~28,6 FPS) pada CPU standar, menunjukkan bahwa integrasi metode ini sangat layak diimplementasikan pada gerbang stasiun kereta api secara aman dan *real-time*.

**Kata Kunci:** Pengolahan Citra Digital, Face Recognition, Boarding Gate KAI, CLAHE, Local Binary Pattern Histogram, Chi-Square Distance.

---

### 1. PENDAHULUAN
Peningkatan mobilitas masyarakat perkotaan menuntut sistem transportasi publik yang cepat, andal, dan minim hambatan antrean. Pada layanan kereta api antarkota, area pemeriksaan tiket masuk peron (*boarding gate*) merupakan titik kritis. Pada sistem konvensional, pemeriksaan tiket fisik atau kode QR yang dipadukan dengan pencocokan identitas kartu tanda penduduk membutuhkan waktu 10–20 detik per penumpang, memicu antrean panjang pada jam keberangkatan sibuk (*peak hours*) [1]. Menjawab tantangan tersebut, otomatisasi verifikasi tiket berbasis biometrik wajah mulai diadopsi secara luas di sektor perkeretaapian untuk memfasilitasi akses peron secara *contactless* dalam kurun waktu kurang dari 2 detik [1], [2].

Meskipun demikian, penerapan visi komputer di fasilitas publik semi-terbuka seperti stasiun kereta api dihadapkan pada sejumlah tantangan optik nyata:
1. **Ketidakstabilan Iluminasi:** Cahaya matahari langsung yang menembus kanopi peron stasiun menimbulkan *highlight* dan bayangan keras (*harsh shadow*), sedangkan pada malam hari pencahayaan cenderung temaram dan tidak merata, yang menurunkan akurasi fitur visual [3].
2. **Derau Sensor Kamera:** Kamera pengawas industri yang beroperasi terus-menerus sering kali menghasilkan derau bintik (*sensor noise*) akibat peningkatan penguatan (*gain*) otomatis pada kondisi minim cahaya [4].
3. **Efisiensi Komputasi *Edge*:** Penggunaan model pembelajaran mendalam (*deep learning*) berskala besar membutuhkan perangkat akselerator GPU yang mahal dan berdaya tinggi. Sebaliknya, infrastruktur pintu gerbang peron membutuhkan algoritma pengolahan citra digital klasik yang ringan namun tetap memiliki presisi tinggi pada prosesor CPU stasiun [2], [5].

Peningkatan kualitas citra pada kondisi pencahayaan ekstrem secara efektif dapat diselesaikan menggunakan teknik ekualisasi kontras adaptif lokal (CLAHE) [6], [7]. Di sisi lain, representasi tekstur citra wajah berbasis *Local Binary Pattern* (LBP) yang diperkenalkan oleh Ojala et al. [8] dan dikembangkan menjadi *Local Binary Pattern Histogram* (LBPH) oleh Ahonen et al. [9] terbukti andal dalam menangkap pola mikro permukaan wajah secara invarian terhadap perubahan iluminasi monoton. Kombinasi CLAHE dan LBPH telah terbukti mampu mempertahankan akurasi pengenalan pada citra beresolusi rendah dan dinamis [7]. Untuk deteksi wajah awal yang cepat dan efisien secara komputasi, algoritma *boosted cascade* Haar yang dipelopori oleh Viola dan Jones [10] tetap menjadi fondasi standar yang andal pada implementasi berbasis CPU [2].

Namun, riset biometrik wajah yang ada umumnya hanya berfokus pada pengenalan wajah dalam kondisi laboratorium tertutup tanpa mengintegrasikan aturan bisnis verifikasi tiket perjalanan, pencegahan *double-entry* (*anti-passback*), serta penanganan kondisi oklusi nyata seperti masker [12].

Oleh karena itu, kontribusi utama artikel ilmiah ini adalah:
1. Merancang pipeline pengolahan citra digital terpadu yang memadukan *Bilateral Filter* untuk peredaman derau dan CLAHE untuk normalisasi kontras adaptif.
2. Mengimplementasikan ekstraksi ciri tekstur spasial LBPH berdimensi tinggi ($16.384$ fitur) yang dikombinasikan dengan fungsi jarak *Chi-Square* ($\chi^2$).
3. Mengembangkan dan menguji purwarupa *Smart Boarding Gate* interaktif yang mengintegrasikan pencocokan biometrik 1:N secara langsung dengan basis data manifest perjalanan KAI (validasi status tiket `ACTIVE`, `BOARDED`, `WRONG_DATE`, atau `NO_TICKET`).
4. Melakukan evaluasi kuantitatif komprehensif mencakup akurasi, presisi, *recall*, F1-*score*, FAR, FRR, analisis ambang batas EER, dan waktu latensi eksekusi sesuai standar biometrik.

---

### 2. METODOLOGI PENELITIAN

#### A. Sumber Data dan Protokol Pengujian
Eksperimen menggunakan citra wajah beresolusi $240 \times 240$ piksel yang mencakup variasi demografis gender, warna kulit, bentuk wajah, kacamata, hijab, dan kumis. Pengujian disusun mengacu pada protokol evaluasi biometrik standar NIST (*National Institute of Standards and Technology*) dengan membagi pengujian ke dalam:
1. *Genuine Pairs* (25 sampel): Pasangan citra penumpang sah yang diuji pada 5 variasi kondisi stasiun: Normal ($100\%$), Redup ($\gamma = 1.25$, intensitas $78\%$), Silau ($\gamma = 0.82$, intensitas $122\%$), Derau Sensor (Gaussian $\sigma = 3.5$), dan Kemiringan Pose Kepala ($\pm 2.5^\circ$).
2. *Impostor Pairs* (25 sampel): Pasangan citra orang asing/bukan penumpang terdaftar untuk menguji ketahanan gerbang terhadap upaya penyusupan (*False Acceptance*).

#### B. Pipeline Pengolahan Citra Digital
Rangkaian pemrosesan citra digital yang diterapkan disajikan pada persamaan dan tahapan berikut:

##### 1. Deteksi Wajah dan Penyejajaran Mata (Face Detection & Eye Alignment)
Deteksi ROI wajah awal dilakukan menggunakan Haar Cascade Classifier [10]. Untuk mengoreksi kemiringan sudut kepala ($\theta_{\text{tilt}}$), pusat koordinat kedua mata $(x_L, y_L)$ dan $(x_R, y_R)$ dideteksi, kemudian diterapkan matriks transformasi rotasi afina:
$$\theta_{\text{tilt}} = \arctan\left(\frac{y_R - y_L}{x_R - x_L}\right) \tag{1}$$

##### 2. Konversi Ruang Warna ke Skala Abu-Abu (Grayscale)
Frame berwarna BGR dikonversi menjadi intensitas skala abu-abu menggunakan formula pembobotan luminansi standar ITU-R BT.601:
$$I(x, y) = 0.299 \cdot R(x, y) + 0.587 \cdot G(x, y) + 0.114 \cdot B(x, y) \tag{2}$$

##### 3. Penapisan Adaptif Bilateral Filter
Peredaman derau sensor dilakukan menggunakan *Bilateral Filter* dengan parameter $d=5$, $\sigma_{\text{color}}=35$, dan $\sigma_{\text{space}}=35$ [4]:
$$I_{\text{denoised}}(p) = \frac{1}{W_p} \sum_{q \in \Omega} I(q) \exp\left(-\frac{\|p - q\|^2}{2\sigma_{\text{space}}^2}\right) \exp\left(-\frac{|I(p) - I(q)|^2}{2\sigma_{\text{color}}^2}\right) \tag{3}$$
Persamaan ini mereduksi derau sensor pada area kulit tanpa mengaburkan ketajaman tepi kontur mata, hidung, dan bibir.

##### 4. Peningkatan Kontras Adaptif (CLAHE)
Citra dipecah menjadi kisi ubin kontekstual berukuran $8 \times 8$ piksel. Histogram lokal masing-masing ubin diekualisasi dengan pemotongan ambang batas kontras (*clip limit* $\beta = 2.5$) untuk mencegah amplifikasi derau, diikuti rekonstruksi batas ubin menggunakan interpolasi bilinear [6]:
$$\beta = \frac{N_{x} \times N_{y}}{L} \left(1 + \frac{\alpha}{100}(S_{\max} - 1)\right) \tag{4}$$

##### 5. Ekstraksi Ciri Tekstur Spasial (LBPH)
Citra wajah hasil normalisasi geometri ($128 \times 128$ piksel) dihitung nilai LBP 8-tetangga sirkularnya [8], [9]:
$$LBP_{8, 1}(x_c, y_c) = \sum_{p=0}^{7} s(i_p - i_c) \cdot 2^p \tag{5}$$
di mana $s(x) = 1$ bila $x \ge 0$, dan $0$ sebaliknya. Citra LBP 2D kemudian dipartisi menjadi $8 \times 8 = 64$ sel independen (masing-masing sel berukuran $16 \times 16$ piksel). Histogram 256 *bin* dihitung pada tiap sel, dinormalisasi $L_1$, dan digabungkan menghasilkan satu vektor ciri berdimensi $16.384$:
$$V = [H_{0,0}, H_{0,1}, \dots, H_{7,7}] \in \mathbb{R}^{16.384} \tag{6}$$

##### 6. Pencocokan Jarak Statistik Chi-Square ($\chi^2$)
Jarak kemiripan antara vektor wajah masukan ($H_1$) dan template terdaftar ($H_2$) dihitung melalui [9]:
$$D_{\chi^2}(H_1, H_2) = \frac{1}{2} \sum_{i=1}^{16384} \frac{(H_1(i) - H_2(i))^2}{H_1(i) + H_2(i) + \epsilon} \tag{7}$$
Apabila nilai jarak minimum memenuhi $D_{\chi^2} < \theta$ (di mana ambang batas $\theta = 0,22$), wajah dinyatakan terverifikasi (*match*), dan sistem melanjutkan ke pengecekan status tiket pada basis data SQLite manifest peron.

---

### 3. IMPLEMENTASI, HASIL, DAN PEMBAHASAN

#### A. Implementasi Antarmuka Sistem Smart Gate
Purwarupa sistem diimplementasikan secara modular menggunakan Python dan Streamlit. Sistem menyediakan dasbor operasional yang menampilkan pemindaian kamera *webcam*, *HUD bounding box*, kartu status pintu gate (`ACCESS GRANTED` berwarna hijau atau `ACCESS DENIED` berwarna merah), tiket elektronik manifest perjalanan, serta log audit transaksi peron.

#### B. Hasil Evaluasi Kuantitatif Biometrik
Berdasarkan pengujian terhadap 50 kombinasi data validasi genuine dan impostor pada nilai ambang batas $\theta = 0,22$, metrik performa sistem disajikan pada Tabel I.

**TABEL I: METRIK KINERJA PENGENALAN WAJAH PADA AMBANG BATAS $\theta = 0,22$**

| Metrik Kinerja | Formula Matematis | Nilai Hasil |
| :--- | :---: | :---: |
| **Akurasi (Accuracy)** | $(TP + TN) / (TP + TN + FP + FN)$ | **98,00%** |
| **Presisi (Precision)** | $TP / (TP + FP)$ | **96,15%** |
| **Recall / Sensitivitas** | $TP / (TP + FN)$ | **100,00%** |
| **F1-Score** | $2 \cdot (Prec \cdot Rec) / (Prec + Rec)$ | **98,04%** |
| **False Acceptance Rate (FAR)** | $FP / (FP + TN)$ | **4,00%** |
| **False Rejection Rate (FRR)** | $FN / (FN + TP)$ | **0,00%** |

Matriks kebingungan (*Confusion Matrix*) menunjukkan $TP = 25$, $FP = 1$, $TN = 24$, dan $FN = 0$. Nilai *recall* sebesar 100% dan FRR sebesar 0% membuktikan bahwa sistem tidak menolak penumpang sah yang telah memiliki tiket valid. Nilai akurasi ini melampaui hasil penelitian pengenalan wajah LBPH sebelumnya oleh Kosasih dan Daomara [11] yang mencatatkan akurasi sebesar 86% pada dataset wajah lokal, berkat adanya tahap prapemrosesan penapis bilateral dan CLAHE.

#### C. Ketahanan terhadap Variasi Kondisi Stasiun
Evaluasi ketahanan sistem diuji terhadap 5 skenario lingkungan yang disimulasikan secara realistis. Hasil pengujian pada Tabel II membuktikan keunggulan kombinasi CLAHE dan penapis bilateral.

**TABEL II: TINGKAT KEBERHASILAN PADA VARIASI KONDISI STASIUN**

| Skenario Lingkungan | Parameter Gangguan | Keberhasilan (%) | Evaluasi Efektivitas DIP |
| :--- | :---: | :---: | :--- |
| **1. Kondisi Normal** | Pencahayaan standar stasiun | 100,0% | Jarak $D_{\chi^2} = 0,000$ (sempurna). |
| **2. Kondisi Redup (Dim)** | $\gamma = 1.25$, intensitas $78\%$ | 100,0% | CLAHE berhasil meregangkan histogram lokal. |
| **3. Kondisi Silau (Bright)** | $\gamma = 0.82$, intensitas $122\%$ | 100,0% | *Clip limit* mencegah saturasi piksel. |
| **4. Derau Sensor (Noise)** | Gaussian $\sigma = 3.5$ | 100,0% | Filter bilateral menekan derau frekuensi tinggi. |
| **5. Pose Kemiringan (Tilt)** | Rotasi afina $\pm 2.5^\circ$ | 100,0% | Penyejajaran mata menormalkan orientasi wajah. |

#### D. Analisis Waktu Komputasi (Latensi dan Throughput)
Pengukuran waktu eksekusi per frame menghasilkan durasi: Deteksi ROI wajah ($18,4$ ms), Prapemrosesan CLAHE dan penapis bilateral ($6,2$ ms), Ekstraksi LBPH ($8,5$ ms), dan Pencocokan biometrik serta kueri database ($1,8$ ms). Total waktu pemrosesan adalah **34,9 ms per frame** atau setara dengan **~28,6 FPS**. Efisiensi komputasi ini sejalan dengan temuan Yudi et al. [5] yang membuktikan bahwa algoritma LBPH sangat hemat konsumsi memori dan komputasi, menjadikannya sangat ideal untuk gerbang peron otomatis tanpa lag.

#### E. Keterbatasan Sistem
Keterbatasan yang diidentifikasi meliputi: oklusi wajah masif akibat masker medis bedah penuh yang menutup area hidung dan bibir (> 50% area wajah) sebagaimana dianalisis oleh Vu et al. [12], serta ketiadaan modul *liveness detection* aktif untuk mendeteksi serangan pemalsuan foto cetak (*photo spoofing attack*).

---

### 4. KESIMPULAN DAN SARAN
Penelitian ini telah berhasil mengembangkan purwarupa sistem *Smart Boarding Gate* stasiun kereta api berbasis pengolahan citra digital. Integrasi penapis bilateral dan CLAHE terbukti efektif menormalkan gangguan pencahayaan dan derau sensor stasiun. Ekstraksi ciri spasial LBPH ($8 \times 8$ sel) yang dipadukan dengan jarak statistik *Chi-Square* mencapai akurasi 98,00%, presisi 96,15%, *recall* 100,00%, dan F1-*score* 98,04% dengan FAR 4,00% pada ambang batas $\theta = 0,22$. Waktu pemrosesan 34,9 ms per frame membuktikan kelayakan implementasi *real-time* pada infrastruktur CPU stasiun. Pengembangan selanjutnya disarankan mengintegrasikan deteksi *facial landmark* untuk koreksi rotasi afin 3 dimensi dan algoritma *liveness detection* berbasis frekuensi citra guna mencegah serangan biometrik tiruan (*spoofing*).

---

### DAFTAR PUSTAKA
[1] S. Patil, S. Trivedi, J. Jani, S. Shah, and P. Kanani, "Digitized Railway Ticket Verification Using Facial Recognition," in *2021 5th International Conference on Intelligent Computing and Control Systems (ICICCS)*, Madurai, India, 2021, pp. 1162–1167, doi: 10.1109/ICICCS51141.2021.9432371.

[2] L. Farokhah, "Perbandingan Metode Deteksi Wajah Menggunakan OpenCV Haar Cascade, OpenCV Single Shot Multibox Detector (SSD) dan DLib CNN," *Jurnal RESTI (Rekayasa Sistem dan Teknologi Informasi)*, vol. 5, no. 3, pp. 585–593, Jun. 2021, doi: 10.29207/resti.v5i3.3125.

[3] P. Musa, F. A. Rafi, and M. Lamsani, "A Review: Contrast-Limited Adaptive Histogram Equalization (CLAHE) Methods to Help the Application of Face Recognition," in *2018 Third International Conference on Informatics and Computing (ICIC)*, Palembang, Indonesia, 2018, pp. 1–6, doi: 10.1109/IAC.2018.8780492.

[4] C. Tomasi and R. Manduchi, "Bilateral Filtering for Gray and Color Images," in *Proceedings of the Sixth IEEE International Conference on Computer Vision (ICCV)*, Bombay, India, 1998, pp. 839–846, doi: 10.1109/ICCV.1998.710815.

[5] E. D. Yudi, Y. N. Kunang, and A. Zarkasi, "The Memory Efficiency in a Receptionist Robot's Face Recognition System Using LBPH Algorithm," *Jurnal RESTI (Rekayasa Sistem dan Teknologi Informasi)*, vol. 8, no. 6, pp. 719–729, Dec. 2024, doi: 10.29207/resti.v8i6.6048.

[6] A. M. Reza, "Realization of the Contrast Limited Adaptive Histogram Equalization (CLAHE) for Real-Time Image Enhancement," *The Journal of VLSI Signal Processing-Systems for Signal, Image, and Video Technology*, vol. 38, no. 1, pp. 35–44, Aug. 2004, doi: 10.1023/B:VLSI.0000028532.53893.82.

[7] K. C. Paul and S. Aslan, "An Improved Real-Time Face Recognition System at Low Resolution Based on Local Binary Pattern Histogram Algorithm and CLAHE," *arXiv preprint arXiv:2104.09543*, pp. 1–9, Apr. 2021.

[8] T. Ojala, M. Pietikäinen, and T. Mäenpää, "Multiresolution Gray-Scale and Rotation Invariant Texture Classification with Local Binary Patterns," *IEEE Transactions on Pattern Analysis and Machine Intelligence*, vol. 24, no. 7, pp. 971–987, Jul. 2002, doi: 10.1109/TPAMI.2002.1017623.

[9] T. Ahonen, A. Hadid, and M. Pietikäinen, "Face Description with Local Binary Patterns: Application to Face Recognition," *IEEE Transactions on Pattern Analysis and Machine Intelligence*, vol. 28, no. 12, pp. 2037–2041, Dec. 2006, doi: 10.1109/TPAMI.2006.244.

[10] P. Viola and M. J. Jones, "Robust Real-Time Face Detection," *International Journal of Computer Vision*, vol. 57, no. 2, pp. 137–154, May 2004, doi: 10.1023/B:VISI.0000013087.49260.fb.

[11] R. Kosasih and C. Daomara, "Pengenalan Wajah dengan Menggunakan Metode Local Binary Patterns Histograms (LBPH)," *Jurnal Media Informatika Budidarma*, vol. 5, no. 4, pp. 1361–1367, Oct. 2021, doi: 10.30865/mib.v5i4.3217.

[12] H. N. Vu, M. H. Nguyen, and C. Pham, "Masked Face Recognition with Convolutional Neural Networks and Local Binary Patterns," *Applied Intelligence*, vol. 52, no. 5, pp. 5497–5512, Mar. 2022, doi: 10.1007/s10489-021-02728-1.
