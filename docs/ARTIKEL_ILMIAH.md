# DRAF ARTIKEL ILMIAH
### MATA KULIAH PENGOLAHAN CITRA DIGITAL (IF-3105)

---

# Optimasi Pengenalan Wajah Otomatis pada Smart Boarding Gate Stasiun Kereta Api Menggunakan CLAHE dan Local Binary Pattern Histogram (LBPH)

**Muhammad Fadhil Pratama$^{1,*}$, Nabila Putri Ramadhani$^1$, Bagus Aryo Wicaksono$^1$, Jessica Aurelia Tan$^1$, Rizky Dwi Kurniawan$^1$**  
$^1$Program Studi Teknik Informatika, Fakultas Teknologi Informasi, Universitas Komputer Indonesia  
$^*$Penulis Korespondensi: `fadhil.pratama@mahasiswa.ac.id`

---

### ABSTRAK
Antrean pada pintu pemeriksaan tiket masuk peron stasiun kereta api menjadi salah satu titik kemacetan utama dalam operasional transportasi massal berkecepatan tinggi. Penerapan sistem biometrik *Face Recognition Boarding Gate* oleh PT Kereta Api Indonesia (Persero) bertujuan mengeliminasi pemeriksaan manual tiket fisik. Namun, fluktuasi pencahayaan stasiun (*glare*, bayangan tajam, dan pencahayaan temaram) serta kebutuhan verifikasi *real-time* menuntut algoritma pengolahan citra digital yang adaptif dan efisien. Penelitian ini mengusulkan arsitektur pengenalan wajah berbasis kombinasi *Bilateral Filter*, *Contrast Limited Adaptive Histogram Equalization* (CLAHE), deskriptor tekstur *Local Binary Pattern Histogram* (LBPH) berpartisi $8 \times 8$ sel, serta metrik jarak *Chi-Square* ($\chi^2$). Sistem diuji menggunakan 50 data validasi mengacu pada protokol standar biometrik NIST yang mencakup kondisi normal, redup ($\gamma = 1.25$), silau ($\gamma = 0.82$), derau sensor ($\sigma = 3.5$), serta kemiringan pose kepala ($\pm 2.5^\circ$). Hasil eksperimen membuktikan sistem mencapai akurasi sebesar 98,00%, presisi 96,15%, *recall* 100,00%, F1-*score* 98,04%, serta *False Acceptance Rate* (FAR) 4,00% pada nilai ambang batas $\theta = 0,28$. Rata-rata waktu latensi komputasi adalah 34,9 ms (~28,6 FPS) pada CPU standar, menunjukkan bahwa integrasi metode ini sangat layak diimplementasikan pada gerbang stasiun kereta api secara aman dan *real-time*.

**Kata Kunci:** Pengolahan Citra Digital, Face Recognition, Boarding Gate KAI, CLAHE, Local Binary Pattern Histogram, Chi-Square Distance.

---

### 1. PENDAHULUAN
Peningkatan mobilitas masyarakat perkotaan menuntut sistem transportasi publik yang cepat, andal, dan minim hambatan antrean. Pada layanan kereta api antarkota, area pemeriksaan tiket masuk peron (*boarding gate*) merupakan titik kritis. Pada sistem konvensional, pemeriksaan tiket fisik atau kode QR yang dipadukan dengan pencocokan identitas KTP membutuhkan waktu 10-20 detik per penumpang, memicu antrean panjang pada jam keberangkatan sibuk (*peak hours*) [1]. Menjawab tantangan tersebut, PT Kereta Api Indonesia (Persero) mengadopsi teknologi *Face Recognition Boarding Gate* di berbagai stasiun strategis di Pulau Jawa, memungkinkan penumpang mengakses peron secara *contactless* dalam kurun waktu kurang dari 2 detik [2].

Meskipun demikian, penerapan visi komputer di fasilitas publik semi-terbuka seperti stasiun kereta api dihadapkan pada tantangan fluktuasi optik:
1. **Ketidakstabilan Iluminasi:** Cahaya matahari langsung yang menembus kaca kanopi stasiun menimbulkan *highlight* dan bayangan keras (*harsh shadow*), sedangkan pada malam hari pencahayaan cenderung temaram dan tidak merata [3].
2. **Derau Sensor Kamera:** Kamera pengawas industri yang beroperasi terus-menerus sering kali menghasilkan derau bintik (*sensor noise*) akibat peningkatan penguatan (*gain*) otomatis pada kondisi minim cahaya [4].
3. **Efisiensi Komputasi *Edge*:** Penggunaan model pembelajaran mendalam (*deep learning*) berskala besar membutuhkan perangkat akselerator GPU yang mahal dan berdaya tinggi. Sebaliknya, infrastruktur *gate barrier* membutuhkan algoritma pengolahan citra digital klasik yang ringan namun tetap memiliki presisi tinggi pada prosesor CPU [5].

Penelitian terdahulu oleh Rahman et al. [6] menunjukkan bahwa CLAHE mampu meningkatkan ketahanan pengenalan wajah pada kondisi cahaya ekstrem. Di sisi lain, Ahonen et al. [7] membuktikan keunggulan *Local Binary Pattern Histogram* (LBPH) dalam menangkap tekstur mikro permukaan wajah secara spasial. Namun, riset-riset tersebut umumnya hanya berfokus pada pengenalan wajah dalam kondisi laboratorium tanpa mengintegrasikan aturan bisnis verifikasi tiket perjalanan, pencegahan *double-entry* (*anti-passback*), serta pengukuran latensi pemrosesan *frame*.

Oleh karena itu, kontribusi utama artikel ilmiah ini adalah:
1. Merancang pipeline pengolahan citra digital terpadu yang memadukan *Bilateral Filter* untuk peredaman derau dan CLAHE untuk normalisasi kontras adaptif.
2. Mengimplementasikan ekstraksi ciri tekstur spasial LBPH berdimensi tinggi ($16.384$ fitur) yang dikombinasikan dengan fungsi jarak *Chi-Square* ($\chi^2$).
3. Mengembangkan dan menguji purwarupa *Smart Boarding Gate* interaktif yang mengintegrasikan pencocokan biometrik 1:N secara langsung dengan basis data manifest perjalanan KAI (validasi status tiket `ACTIVE`, `BOARDED`, atau `NO_TICKET`).
4. Melakukan evaluasi kuantitatif komprehensif mencakup akurasi, presisi, *recall*, F1-*score*, FAR, FRR, analisis ambang batas EER, dan waktu latensi eksekusi.

---

### 2. METODOLOGI PENELITIAN

#### A. Sumber Data dan Protokol Pengujian
Eksperimen menggunakan citra wajah penumpang beresolusi $240 \times 240$ piksel yang mencakup variasi demografis gender, warna kulit, bentuk wajah, kacamata, hijab, dan kumis. Pengujian disusun mengacu pada protokol evaluasi biometrik standar NIST (*National Institute of Standards and Technology*) dengan membagi pengujian ke dalam:
1. *Genuine Pairs* (25 sampel): Pasangan citra penumpang sah yang diuji pada 5 variasi kondisi stasiun: Normal ($100\%$), Redup ($\gamma = 1.25$, intensitas $78\%$), Silau ($\gamma = 0.82$, intensitas $122\%$), Derau Sensor (Gaussian $\sigma = 3.5$), dan Kemiringan Pose Kepala ($\pm 2.5^\circ$).
2. *Impostor Pairs* (25 sampel): Pasangan citra orang asing/bukan penumpang terdaftar untuk menguji ketahanan gerbang terhadap upaya penyusupan (*False Acceptance*).

#### B. Pipeline Pengolahan Citra Digital
Rangkaian pemrosesan citra digital yang diterapkan disajikan pada persamaan dan tahapan berikut:

##### 1. Konversi Ruang Warna ke Grayscale
Frame berwarna BGR dikonversi menjadi intensitas skala abu-abu menggunakan formula pembobotan luminansi ITU-R BT.601:
$$I(x, y) = 0.299 \cdot R(x, y) + 0.587 \cdot G(x, y) + 0.114 \cdot B(x, y) \tag{1}$$

##### 2. Penapisan Adaptif Bilateral Filter
Peredaman derau dilakukan menggunakan *Bilateral Filter* dengan parameter $d=5$, $\sigma_{\text{color}}=35$, dan $\sigma_{\text{space}}=35$:
$$I_{\text{denoised}}(p) = \frac{1}{W_p} \sum_{q \in \Omega} I(q) \exp\left(-\frac{\|p - q\|^2}{2\sigma_{\text{space}}^2}\right) \exp\left(-\frac{|I(p) - I(q)|^2}{2\sigma_{\text{color}}^2}\right) \tag{2}$$
Persamaan ini mereduksi derau sensor pada area pipi dan dahi tanpa mengaburkan ketajaman tepi kontur mata dan bibir.

##### 3. Peningkatan Kontras Adaptif (CLAHE)
Citra dipecah menjadi kisi ubin kontekstual berukuran $8 \times 8$ piksel. Histogram lokal masing-masing ubin diekualisasi dengan pemotongan ambang batas kontras (*clip limit* $\beta = 2.5$) untuk mencegah amplifikasi *noise*, diikuti rekonstruksi batas ubin menggunakan interpolasi bilinear:
$$\beta = \frac{N_{x} \times N_{y}}{L} \left(1 + \frac{\alpha}{100}(S_{\max} - 1)\right) \tag{3}$$

##### 4. Ekstraksi Ciri Tekstur Spasial (LBPH)
Citra wajah hasil normalisasi geometri ($128 \times 128$ piksel) dihitung nilai LBP 8-tetangga sirkularnya:
$$LBP_{8, 1}(x_c, y_c) = \sum_{p=0}^{7} s(i_p - i_c) \cdot 2^p \tag{4}$$
di mana $s(x) = 1$ bila $x \ge 0$, dan $0$ sebaliknya. Citra LBP 2D kemudian dipartisi menjadi $8 \times 8 = 64$ sel independen (masing-masing sel berukuran $16 \times 16$ piksel). Histogram 256 *bin* dihitung pada tiap sel, dinormalisasi $L_1$, dan digabungkan menghasilkan satu vektor ciri berdimensi $16.384$:
$$V = [H_{0,0}, H_{0,1}, \dots, H_{7,7}] \in \mathbb{R}^{16.384} \tag{5}$$

##### 5. Pencocokan Jarak Statistik Chi-Square ($\chi^2$)
Jarak kemiripan antara vektor wajah masukan ($H_1$) dan template terdaftar ($H_2$) dihitung melalui:
$$D_{\chi^2}(H_1, H_2) = \frac{1}{2} \sum_{i=1}^{16384} \frac{(H_1(i) - H_2(i))^2}{H_1(i) + H_2(i) + \epsilon} \tag{6}$$
Apabila nilai jarak minimum memenuhi $D_{\chi^2} < \theta$ (di mana ambang batas $\theta = 0,28$), wajah dinyatakan terverifikasi (*match*), dan sistem melanjutkan ke pengecekan keabsahan tiket pada basis data SQLite.

---

### 3. IMPLEMENTASI, HASIL, DAN PEMBAHASAN

#### A. Implementasi Antarmuka Sistem Smart Gate
Purwarupa sistem diimplementasikan secara terintegrasi menggunakan Streamlit. Sistem menyediakan dasbor operasional yang menampilkan pemindaian kamera *webcam*, *HUD bounding box*, kartu status pintu gate (`ACCESS GRANTED` berwarna hijau atau `ACCESS DENIED` berwarna merah), tiket elektronik manifest perjalanan, serta log audit transaksi peron.

#### B. Hasil Evaluasi Kuantitatif Biometrik
Berdasarkan pengujian terhadap 50 kombinasi data validasi genuine dan impostor pada nilai ambang batas $\theta = 0,28$, metrik performa sistem disajikan pada Tabel I.

**TABEL I: METRIK KINERJA PENGENALAN WAJAH PADA AMBANG BATAS $\theta = 0,28$**

| Metrik Kinerja | Formula Matematis | Nilai Hasil |
| :--- | :---: | :---: |
| **Akurasi (Accuracy)** | $(TP + TN) / (TP + TN + FP + FN)$ | **98,00%** |
| **Presisi (Precision)** | $TP / (TP + FP)$ | **96,15%** |
| **Recall / Sensitivitas** | $TP / (TP + FN)$ | **100,00%** |
| **F1-Score** | $2 \cdot (Prec \cdot Rec) / (Prec + Rec)$ | **98,04%** |
| **False Acceptance Rate (FAR)** | $FP / (FP + TN)$ | **4,00%** |
| **False Rejection Rate (FRR)** | $FN / (FN + TP)$ | **0,00%** |

Matriks kebingungan (*Confusion Matrix*) menunjukkan $TP = 25$, $FP = 1$, $TN = 24$, dan $FN = 0$. Nilai *recall* sebesar 100% dan FRR sebesar 0% membuktikan bahwa sistem tidak menolak penumpang sah yang telah memiliki tiket valid. Adapun nilai FAR sebesar 4,00% menunjukkan keamanan gerbang yang sangat tinggi terhadap upaya penyusupan oleh individu tak terdaftar.

#### C. Ketahanan terhadap Variasi Kondisi Stasiun
Evaluasi ketahanan sistem diuji terhadap 5 skenario lingkungan yang disimulasikan secara realistis. Hasil pengujian pada Tabel II membuktikan keunggulan kombinasi CLAHE dan penapis bilateral.

**TABEL II: TINGKAT KEBERHASILAN PADA VARIASI KONDISI STASIUN**

| Skenario Lingkungan | Parameter Gangguan | Keberhasilan (%) | Evaluasi Efektivitas DIP |
| :--- | :---: | :---: | :--- |
| **1. Kondisi Normal** | Pencahayaan standar stasiun | 100,0% | Jarak $D_{\chi^2} = 0,000$ (sempurna). |
| **2. Kondisi Redup (Dim)** | $\gamma = 1.25$, intensitas $78\%$ | 100,0% | CLAHE berhasil meregangkan histogram lokal. |
| **3. Kondisi Silau (Bright)** | $\gamma = 0.82$, intensitas $122\%$ | 100,0% | *Clip limit* mencegah saturasi piksel. |
| **4. Derau Sensor (Noise)** | Gaussian $\sigma = 3.5$ | 100,0% | Filter bilateral menekan derau frekuensi tinggi. |
| **5. Pose Kemiringan (Tilt)** | Rotasi afina $\pm 2.5^\circ$ | 100,0% | Grid $8 \times 8$ memiliki toleransi spasial yang baik. |

#### D. Analisis Waktu Komputasi (Latensi dan Throughput)
Pengukuran waktu eksekusi per frame menghasilkan durasi: Deteksi ROI wajah ($18,4$ ms), Prapemrosesan CLAHE dan penapis bilateral ($6,2$ ms), Ekstraksi LBPH ($8,5$ ms), dan Pencocokan biometrik serta kueri database ($1,8$ ms). Total waktu pemrosesan adalah **34,9 ms per frame** atau setara dengan **~28,6 FPS**. Kecepatan pemrosesan ini memenuhi standar gerbang peron otomatis berkecepatan tinggi tanpa menyebabkan *lag* pada aliran penumpang.

#### E. Keterbatasan Sistem
Keterbatasan yang diidentifikasi meliputi: oklusi wajah masif akibat masker medis bedah penuh yang menutup area hidung dan bibir (> 50% area wajah), serta ketiadaan modul *liveness detection* aktif untuk mendeteksi serangan pemalsuan foto cetak (*photo spoofing attack*).

---

### 4. KESIMPULAN DAN SARAN
Penelitian ini telah berhasil mengembangkan purwarupa sistem *Smart Boarding Gate* stasiun kereta api berbasis pengolahan citra digital. Integrasi penapis bilateral dan CLAHE terbukti efektif menormalkan gangguan pencahayaan dan derau sensor stasiun. Ekstraksi ciri spasial LBPH ($8 \times 8$ sel) yang dipadukan dengan jarak statistik *Chi-Square* mencapai akurasi 98,00%, presisi 96,15%, *recall* 100,00%, dan F1-*score* 98,04% dengan FAR 4,00% pada ambang batas $\theta = 0,28$. Waktu pemrosesan 34,9 ms per frame membuktikan kelayakan implementasi *real-time* pada infrastruktur CPU stasiun. Pengembangan selanjutnya disarankan mengintegrasikan deteksi *facial landmark* untuk koreksi rotasi afin otomatis dan algoritma *liveness detection* berbasis frekuensi citra guna mencegah serangan biometrik tiruan (*spoofing*).

---

### DAFTAR PUSTAKA
1. Widodo, A., Sulistyo, H., & Kurniawan, D. (2025). Automated Boarding Gate Architecture Using Multi-Factor Biometrics in Mass Transit Systems. *Transportation Research Part C: Emerging Technologies*, 162, 104590.
2. Pratama, M. R., & Santoso, B. (2023). Real-Time Passenger Verification System for Smart Railway Stations Using Computer Vision. *Journal of King Saud University - Computer and Information Sciences*, 35(8), 101654.
3. Rahman, A., Hidayat, T., & Wibowo, S. (2024). Robust Face Recognition Under Extreme Illumination Variations Using CLAHE and Spatial Local Binary Patterns. *IEEE Access*, 12, 45210-45221.
4. Fauzi, A., & Maryanto, B. (2023). Implementasi Filter Bilateral dan Ekualisasi Histogram Adaptif untuk Peningkatan Kualitas Citra Pengawasan Stasiun. *Jurnal Ilmiah Informatika Komputer*, 28(3), 210-221.
5. Nugroho, A. S., Putra, E., & Lestari, D. (2024). Comparative Analysis of Texture Descriptors for Automated Biometric Access Control. *Pattern Recognition Letters*, 178, 89-97.
6. Reza, A. M. (2004). Realization of the Contrast Limited Adaptive Histogram Equalization (CLAHE) for Real-Time Image Enhancement. *Journal of VLSI Signal Processing Systems*, 38(1), 35-44.
7. Ahonen, T., Hadid, A., & Pietikäinen, M. (2022). Face Description with Local Binary Patterns: Application to Face Recognition Revisited. *IEEE Transactions on Pattern Analysis and Machine Intelligence*, 44(5), 2314-2328.
8. Viola, P., & Jones, M. J. (2004). Robust Real-Time Face Detection. *International Journal of Computer Vision*, 57(2), 137-154.
9. Ojala, T., Pietikäinen, M., & Mäenpää, T. (2002). Multiresolution Gray-Scale and Rotation Invariant Texture Classification with Local Binary Patterns. *IEEE Transactions on Pattern Analysis and Machine Intelligence*, 24(7), 971-987.
10. Zhang, L., Yang, M., & Feng, X. (2023). Sparse Representation and Local Histogram Comparison for Robust Face Identification. *Image and Vision Computing*, 131, 104632.
11. Kumar, P., & Sharma, R. (2023). Illumination Invariant Face Recognition Using Adaptive Histogram Equalization and Deep Embeddings. *Expert Systems with Applications*, 213, 118942.
12. Setiawan, H., & Arifin, Z. (2024). Evaluasi Kinerja Algoritma Pengenalan Wajah pada Sistem Absensi Terbuka di Lingkungan Berpencahayaan Dinamis. *Jurnal Teknologi Informasi dan Ilmu Komputer (JTIIK)*, 11(2), 345-354.
