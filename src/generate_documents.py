import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

import pptx
from pptx.util import Inches as PInches, Pt as PPt
from pptx.dml.color import RGBColor as PRGBColor
from pptx.enum.text import PP_ALIGN

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS_DIR = os.path.join(BASE_DIR, "docs")
EVAL_DIR = os.path.join(BASE_DIR, "data", "evaluation_results")

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    tcPr.append(parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>'))

def generate_laporan_docx():
    doc = docx.Document()

    # Set Margins (Standard 4-4-3-3 cm or 1 inch standard academic)
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1.25)
        section.right_margin = Inches(1)

    # Styles
    normal_style = doc.styles['Normal']
    normal_style.font.name = 'Times New Roman'
    normal_style.font.size = Pt(12)
    normal_style.font.color.rgb = RGBColor(0x22, 0x22, 0x22)

    # 1. HALAMAN JUDUL
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_main = p_title.add_run("TUGAS PROYEK AKHIR\nMATA KULIAH PENGOLAHAN CITRA DIGITAL\n\n")
    r_main.bold = True
    r_main.font.size = Pt(14)

    r_sub = p_title.add_run("PENGEMBANGAN SISTEM SMART BOARDING GATE STASIUN KERETA API MENGGUNAKAN PENGENALAN WAJAH OTOMATIS BERBASIS CLAHE DAN LOCAL BINARY PATTERN HISTOGRAM (LBPH)\n\n\n")
    r_sub.bold = True
    r_sub.font.size = Pt(16)
    r_sub.font.color.rgb = RGBColor(0x1E, 0x2B, 0x58)

    p_group = doc.add_paragraph()
    p_group.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_grp = p_group.add_run("Disusun oleh: Kelompok Pengolahan Citra IF-B\n\n")
    r_grp.bold = True
    r_grp.font.size = Pt(12)

    # Table of authors
    table = doc.add_table(rows=5, cols=3)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    headers = ["No.", "Nama Mahasiswa", "NIM"]
    data = [
        ["1.", "Rafi Dzaka Pratama Putra", "123240104"],
        ["2.", "Raihan Natawangsa", "123240120"],
        ["3.", "Ichsan Wahyu Priambudi", "123240122"],
        ["4.", "Indra Naufal Firdaus", "123240195"],
    ]

    for c_idx, h in enumerate(headers):
        cell = table.cell(0, c_idx)
        cell.text = h
        cell.paragraphs[0].runs[0].bold = True
        set_cell_background(cell, "1E2B58")
        cell.paragraphs[0].runs[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

    for r_idx, row in enumerate(data):
        for c_idx, val in enumerate(row):
            cell = table.cell(r_idx + 1, c_idx)
            cell.text = val
            if r_idx % 2 == 1:
                set_cell_background(cell, "F2F4F8")

    doc.add_paragraph("\n\n")
    p_inst = doc.add_paragraph()
    p_inst.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_inst = p_inst.add_run("PROGRAM STUDI S1 INFORMATIKA\nFAKULTAS TEKNOLOGI INFORMASI\nTAHUN AKADEMIK 2026/2027")
    r_inst.bold = True
    r_inst.font.size = Pt(13)

    doc.add_page_break()

    # 2. KATA PENGANTAR
    h_kp = doc.add_heading("KATA PENGANTAR", level=1)
    h_kp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph(
        "Puji syukur kami panjatkan ke hadirat Tuhan Yang Maha Esa atas rahmat, taufik, dan hidayah-Nya, sehingga Laporan Tugas Proyek Akhir Mata Kuliah Pengolahan Citra Digital dengan judul 'Pengembangan Sistem Smart Boarding Gate Stasiun Kereta Api Menggunakan Pengenalan Wajah Otomatis Berbasis CLAHE dan Local Binary Pattern Histogram (LBPH)' dapat diselesaikan dengan baik dan tepat waktu."
    )
    doc.add_paragraph(
        "Proyek ini dirancang untuk merefleksikan transformasi digital transportasi publik di Indonesia, secara spesifik mengkaji dan mereplikasi prinsip kerja teknologi Face Recognition Boarding Gate yang diimplementasikan oleh PT Kereta Api Indonesia (Persero)."
    )
    p_ttd = doc.add_paragraph("\nBandung / Yogyakarta, November 2026\nTim Penyusun (Kelompok IF-B)")
    p_ttd.alignment = WD_ALIGN_PARAGRAPH.RIGHT

    doc.add_page_break()

    # 3. ABSTRAK
    h_abs = doc.add_heading("ABSTRAK", level=1)
    h_abs.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph(
        "Implementasi fasilitas Face Recognition Boarding Gate oleh PT Kereta Api Indonesia (Persero) telah meningkatkan efisiensi mobilitas penumpang dan meminimalkan antrean pemeriksaan tiket fisik. Namun, kinerja sistem pengenalan wajah pada stasiun kereta dihadapkan pada tantangan variasi iluminasi lingkungan (backlight, bayangan, dan pantulan kaca stasiun) serta latensi komputasi real-time. Penelitian proyek ini bertujuan merancang, mengimplementasikan, dan mengevaluasi sistem smart boarding gate otomatis berbasis pengolahan citra digital dengan mengintegrasikan deteksi Region of Interest (ROI) wajah, penyejajaran mata (eye alignment), prapemrosesan Bilateral Filtering dan Contrast Limited Adaptive Histogram Equalization (CLAHE), ekstraksi ciri tekstur Local Binary Pattern Histogram (LBPH), serta pencocokan biometrik 1:N menggunakan jarak statistik Chi-Square. Sistem diuji menggunakan data validasi foto manusia asli mengacu pada protokol standar biometrik NIST melintasi skenario normal, redup, silau, derau sensor, dan rotasi kepala. Hasil pengujian menunjukkan sistem mencapai nilai akurasi 98,00%, presisi 96,15%, recall 100,00%, F1-score 98,04%, serta False Acceptance Rate (FAR) sebesar 4,00% pada nilai ambang batas theta = 0,22. Rata-rata waktu latensi pemrosesan lengkap adalah 34,9 ms (~28,6 FPS), membuktikan sistem mampu beroperasi secara real-time dan efektif memvalidasi keabsahan manifest tiket kereta api."
    )
    p_kw = doc.add_paragraph()
    r_kw = p_kw.add_run("Kata Kunci: ")
    r_kw.bold = True
    p_kw.add_run("Pengolahan Citra Digital, Face Recognition, Boarding Gate KAI, CLAHE, Local Binary Pattern Histogram (LBPH), Chi-Square Distance, Biometrik Transportasi.")

    doc.add_page_break()

    # BAB I
    doc.add_heading("BAB I: PENDAHULUAN", level=1)
    doc.add_heading("1.1 Latar Belakang", level=2)
    doc.add_paragraph(
        "Transportasi perkeretaapian di Indonesia mengalami modernisasi masif dalam satu dekade terakhir. Sebagai tulang punggung transportasi massal antarkota di Pulau Jawa dan Sumatra, PT Kereta Api Indonesia (Persero) melayani puluhan juta penumpang setiap tahunnya. Seiring tingginya volume mobilitas, area pintu pemeriksaan tiket masuk peron (boarding gate) kerap menjadi titik krusial penumpukan antrean (bottleneck). Pada sistem konvensional, penumpang diwajibkan mencetak boarding pass fisik atau menampilkan kode QR pada aplikasi ponsel, disertai pencocokan identitas fisik melalui e-KTP oleh petugas stasiun secara manual. Proses ini membutuhkan waktu berkisar 10 hingga 20 detik per penumpang dan rentan memicu antrean panjang pada jam keberangkatan sibuk."
    )
    doc.add_paragraph(
        "Untuk mengatasi kendala tersebut, PT Kereta Api Indonesia menerapkan fasilitas Face Recognition Boarding Gate di berbagai stasiun strategis. Namun pada implementasinya di stasiun semi-terbuka, terdapat kendala fluktuasi pencahayaan matahari, silau lampu stasiun, derau sensor kamera, dan kebutuhan verifikasi real-time di bawah 100 milidetik."
    )

    doc.add_heading("1.2 Rumusan Masalah", level=2)
    doc.add_paragraph("1. Bagaimana merancang pipeline pengolahan citra digital yang mampu menormalkan variasi pencahayaan ekstrem stasiun kereta sebelum ekstraksi fitur?")
    doc.add_paragraph("2. Bagaimana mengimplementasikan algoritma Local Binary Pattern Histogram (LBPH) dan penyejajaran mata untuk menghasilkan representasi biometrik wajah yang tangguh?")
    doc.add_paragraph("3. Bagaimana mengintegrasikan pencocokan biometrik 1:N dengan aturan bisnis tiket kereta api (alur registrasi wajah, pemesanan tiket tanpa foto ulang, dan validasi boarding)?")
    doc.add_paragraph("4. Bagaimana performa kuantitatif sistem berdasarkan metrik akurasi, presisi, recall, F1-score, FAR, FRR, dan latensi komputasi?")

    doc.add_heading("1.3 Tujuan Proyek", level=2)
    doc.add_paragraph("1. Mengembangkan modul prapemrosesan citra digital menggunakan konversi luminansi, penyejajaran sudut mata, Filter Bilateral, dan CLAHE.")
    doc.add_paragraph("2. Mengimplementasikan algoritma ekstraksi ciri tekstur spasial LBPH (grid 8x8, 16.384 fitur) dan komparasi Chi-Square secara murni dan efisien.")
    doc.add_paragraph("3. Membangun basis data terintegrasi SQLite dan antarmuka web interaktif Streamlit bertema korporat KAI.")
    doc.add_paragraph("4. Melakukan evaluasi kinerja komprehensif mengacu pada ketentuan pengujian Bagian 9 silabus.")

    # BAB II
    doc.add_heading("BAB II: TINJAUAN PUSTAKA", level=1)
    doc.add_paragraph(
        "Pengenalan wajah (face recognition) adalah cabang visi komputer dan pengolahan citra digital yang memverifikasi atau mengidentifikasi subjek berdasarkan pola spasial wajah. Tahapan utama mencakup konversi Grayscale (bobot luminansi ITU-R BT.601), reduksi derau dengan Filter Bilateral yang mempertahankan ketajaman tepi kontur mata/bibir, serta peningkatan kontras adaptif lokal dengan CLAHE (Contrast Limited Adaptive Histogram Equalization)."
    )
    doc.add_paragraph(
        "Local Binary Pattern (LBP) merepresentasikan hubungan intensitas tiap piksel pusat dengan 8 piksel tetangganya. Pada metode LBPH, citra dibagi ke dalam 64 sel lokal (grid 8x8), dihitung histogramnya, lalu digabungkan menjadi vektor global berdimensi 16.384 fitur. Perbandingan kemiripan antar-vektor dihitung menggunakan rumus statistik Chi-Square Distance."
    )

    # BAB III
    doc.add_heading("BAB III: METODOLOGI PENELITIAN", level=1)
    doc.add_paragraph(
        "Sistem dirancang dengan memisahkan alur registrasi biometrik wajah dan pemesanan tiket kereta api sesuai operasional nyata PT Kereta Api Indonesia. Penumpang mendaftarkan akun dan foto wajah satu kali (Enrolment). Saat memesan tiket di kemudian hari, penumpang cukup memasukkan NIK dan Nama; tiket otomatis terhubung dengan template biometrik wajah sebelumnya. Saat masuk peron, kamera memindai wajah penumpang dan otomatis memvalidasi tiket aktif."
    )

    # Embed Pipeline Stages Image
    stage_img = os.path.join(EVAL_DIR, "pipeline_stages.png")
    if os.path.exists(stage_img):
        doc.add_paragraph("\nGambar 3.1: Tahapan Pipeline Pengolahan Citra Digital (ROI hingga Peta Tekstur LBP):")
        doc.add_picture(stage_img, width=Inches(6.0))

    # BAB IV
    doc.add_heading("BAB IV: HASIL DAN PEMBAHASAN", level=1)
    doc.add_paragraph(
        "Aplikasi web interaktif berhasil diimplementasikan dengan antarmuka Streamlit bertema KAI. Pengujian kuantitatif dilakukan terhadap 50 sampel validasi sesuai protokol NIST melintasi berbagai kondisi lingkungan stasiun."
    )

    # Results Table
    t_res = doc.add_table(rows=8, cols=3)
    t_res.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_headers = ["Metrik Kinerja", "Nilai Hasil", "Keterangan Evaluasi"]
    t_data = [
        ["Akurasi (Overall Accuracy)", "98,00%", "Ketepatan klasifikasi total antara penumpang sah dan penyusup."],
        ["Presisi (Precision)", "96,15%", "Probabilitas subjek yang diizinkan benar-benar penumpang sah."],
        ["Recall (Sensitivitas)", "100,00%", "Kemampuan sistem mengenali seluruh penumpang sah (FRR = 0%)."],
        ["F1-Score", "98,04%", "Keseimbangan harmonik optimal antara presisi dan sensitivitas."],
        ["False Acceptance Rate (FAR)", "4,00%", "Tingkat kesalahan penyusup yang keliru diberi akses."],
        ["False Rejection Rate (FRR)", "0,00%", "Tingkat penolakan keliru terhadap penumpang bertiket aktif."],
        ["Waktu Komputasi per Frame", "34,9 ms", "Eksekusi sangat cepat pada CPU standar (~28,6 FPS / Real-Time)."]
    ]
    for c_idx, h in enumerate(t_headers):
        cell = t_res.cell(0, c_idx)
        cell.text = h
        cell.paragraphs[0].runs[0].bold = True
        set_cell_background(cell, "1E2B58")
        cell.paragraphs[0].runs[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

    for r_idx, row in enumerate(t_data):
        for c_idx, val in enumerate(row):
            cell = t_res.cell(r_idx + 1, c_idx)
            cell.text = val
            if r_idx % 2 == 1:
                set_cell_background(cell, "F2F4F8")

    # Embed Evaluation Plots
    doc.add_paragraph("\nGambar 4.1: Matriks Kebingungan (Confusion Matrix) dan Ketahanan Kondisi Lingkungan Stasiun:")
    cm_img = os.path.join(EVAL_DIR, "confusion_matrix.png")
    rob_img = os.path.join(EVAL_DIR, "condition_robustness.png")
    if os.path.exists(cm_img):
        doc.add_picture(cm_img, width=Inches(3.2))
    if os.path.exists(rob_img):
        doc.add_picture(rob_img, width=Inches(4.5))

    doc.add_paragraph("\nGambar 4.2: Kurva Analisis Ambang Batas FAR-FRR dan Perincian Latensi Komputasi Pipeline:")
    curve_img = os.path.join(EVAL_DIR, "far_frr_curve.png")
    lat_img = os.path.join(EVAL_DIR, "latency_breakdown.png")
    if os.path.exists(curve_img):
        doc.add_picture(curve_img, width=Inches(4.0))
    if os.path.exists(lat_img):
        doc.add_picture(lat_img, width=Inches(4.0))

    # BAB V
    doc.add_heading("BAB V: KESIMPULAN DAN SARAN", level=1)
    doc.add_heading("5.1 Kesimpulan", level=2)
    doc.add_paragraph("1. Purwarupa sistem Smart Boarding Gate otomatis berbasis pengenalan wajah berhasil dibangun dan bekerja terintegrasi dengan database tiket KAI.")
    doc.add_paragraph("2. Penerapan Filter Bilateral, penyejajaran mata, dan CLAHE terbukti efektif menormalkan variasi pencahayaan dan derau sensor stasiun.")
    doc.add_paragraph("3. Algoritma LBPH (16.384 dimensi) dan jarak Chi-Square mencapai akurasi 98,00%, presisi 96,15%, recall 100,00%, dan F1-score 98,04%.")
    doc.add_paragraph("4. Waktu eksekusi rata-rata 34,9 ms (~28,6 FPS) membuktikan sistem sangat andal beroperasi secara real-time pada CPU standar.")

    doc.add_heading("5.2 Saran Pengembangan", level=2)
    doc.add_paragraph("1. Menambahkan modul anti-spoofing pasif / aktif (Liveness Detection) berbasis deteksi kedipan mata guna mencegah serangan foto cetak.")
    doc.add_paragraph("2. Mengintegrasikan model deep embeddings berdaya komputasi rendah (misal MobileFaceNet) untuk kapasitas pencocokan jutaan penumpang.")

    # DAFTAR PUSTAKA
    doc.add_heading("DAFTAR PUSTAKA", level=1)
    refs = [
        "1. Patil, S., Trivedi, S., Jani, J., Shah, S., & Kanani, P. (2021). Digitized Railway Ticket Verification Using Facial Recognition. 2021 5th International Conference on Intelligent Computing and Control Systems (ICICCS), Madurai, India, 1162–1167. https://doi.org/10.1109/ICICCS51141.2021.9432371",
        "2. Farokhah, L. (2021). Perbandingan Metode Deteksi Wajah Menggunakan OpenCV Haar Cascade, OpenCV Single Shot Multibox Detector (SSD) dan DLib CNN. Jurnal RESTI (Rekayasa Sistem dan Teknologi Informasi), 5(3), 585–593. https://doi.org/10.29207/resti.v5i3.3125",
        "3. Musa, P., Rafi, F. A., & Lamsani, M. (2018). A Review: Contrast-Limited Adaptive Histogram Equalization (CLAHE) Methods to Help the Application of Face Recognition. 2018 Third International Conference on Informatics and Computing (ICIC), Palembang, Indonesia, 1–6. https://doi.org/10.1109/IAC.2018.8780492",
        "4. Tomasi, C., & Manduchi, R. (1998). Bilateral Filtering for Gray and Color Images. Proceedings of the Sixth IEEE International Conference on Computer Vision (ICCV), Bombay, India, 839–846. https://doi.org/10.1109/ICCV.1998.710815",
        "5. Yudi, E. D., Kunang, Y. N., & Zarkasi, A. (2024). The Memory Efficiency in a Receptionist Robot's Face Recognition System Using LBPH Algorithm. Jurnal RESTI (Rekayasa Sistem dan Teknologi Informasi), 8(6), 719–729. https://doi.org/10.29207/resti.v8i6.6048",
        "6. Reza, A. M. (2004). Realization of the Contrast Limited Adaptive Histogram Equalization (CLAHE) for Real-Time Image Enhancement. The Journal of VLSI Signal Processing-Systems for Signal, Image, and Video Technology, 38(1), 35–44. https://doi.org/10.1023/B:VLSI.0000028532.53893.82",
        "7. Paul, K. C., & Aslan, S. (2021). An Improved Real-Time Face Recognition System at Low Resolution Based on Local Binary Pattern Histogram Algorithm and CLAHE. arXiv preprint arXiv:2104.09543, 1–9. https://doi.org/10.48550/arXiv.2104.09543",
        "8. Ojala, T., Pietikäinen, M., & Mäenpää, T. (2002). Multiresolution Gray-Scale and Rotation Invariant Texture Classification with Local Binary Patterns. IEEE Transactions on Pattern Analysis and Machine Intelligence, 24(7), 971–987. https://doi.org/10.1109/TPAMI.2002.1017623",
        "9. Ahonen, T., Hadid, A., & Pietikäinen, M. (2006). Face Description with Local Binary Patterns: Application to Face Recognition. IEEE Transactions on Pattern Analysis and Machine Intelligence, 28(12), 2037–2041. https://doi.org/10.1109/TPAMI.2006.244",
        "10. Viola, P., & Jones, M. J. (2004). Robust Real-Time Face Detection. International Journal of Computer Vision, 57(2), 137–154. https://doi.org/10.1023/B:VISI.0000013087.49260.fb",
        "11. Kosasih, R., & Daomara, C. (2021). Pengenalan Wajah dengan Menggunakan Metode Local Binary Patterns Histograms (LBPH). Jurnal Media Informatika Budidarma, 5(4), 1361–1367. https://doi.org/10.30865/mib.v5i4.3217",
        "12. Vu, H. N., Nguyen, M. H., & Pham, C. (2022). Masked Face Recognition with Convolutional Neural Networks and Local Binary Patterns. Applied Intelligence, 52(5), 5497–5512. https://doi.org/10.1007/s10489-021-02728-1"
    ]
    for r in refs:
        p_ref = doc.add_paragraph(r)
        p_ref.paragraph_format.left_indent = Inches(0.4)
        p_ref.paragraph_format.first_line_indent = Inches(-0.4)

    out_file = os.path.join(DOCS_DIR, "LAPORAN_PROYEK_AKHIR.docx")
    doc.save(out_file)
    print(f"Berhasil menghasilkan: {out_file}")

def generate_artikel_docx():
    doc = docx.Document()
    for section in doc.sections:
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.right_margin = Inches(1)

    p_t = doc.add_paragraph()
    p_t.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_t = p_t.add_run("Optimasi Pengenalan Wajah Otomatis pada Smart Boarding Gate Stasiun Kereta Api Menggunakan CLAHE dan Local Binary Pattern Histogram (LBPH)\n")
    r_t.bold = True
    r_t.font.size = Pt(16)
    r_t.font.name = 'Times New Roman'

    p_a = doc.add_paragraph()
    p_a.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_a = p_a.add_run("Rafi Dzaka Pratama Putra, Raihan Natawangsa, Ichsan Wahyu Priambudi, Indra Naufal Firdaus\n")
    r_a.bold = True
    r_a.font.size = Pt(11)
    p_a.add_run("Program Studi S1 Informatika, Fakultas Teknologi Informasi\nKontak Penulis Korespondensi: rafidzaka5@gmail.com\n\n")

    doc.add_heading("ABSTRAK", level=1)
    doc.add_paragraph(
        "Antrean pada pintu pemeriksaan tiket masuk peron stasiun kereta api menjadi salah satu titik kemacetan utama dalam operasional transportasi massal berkecepatan tinggi. Penerapan sistem biometrik Face Recognition Boarding Gate oleh PT Kereta Api Indonesia (Persero) bertujuan mengeliminasi pemeriksaan manual tiket fisik. Namun, fluktuasi pencahayaan stasiun (glare, bayangan tajam, dan pencahayaan temaram) serta kebutuhan verifikasi real-time menuntut algoritma pengolahan citra digital yang adaptif dan efisien. Penelitian ini mengusulkan arsitektur pengenalan wajah berbasis kombinasi penapis bilateral (Bilateral Filter), Contrast Limited Adaptive Histogram Equalization (CLAHE), deskriptor tekstur Local Binary Pattern Histogram (LBPH) berpartisi 8x8 sel, serta metrik jarak Chi-Square. Sistem diuji menggunakan 50 data validasi mengacu pada protokol standar biometrik NIST yang mencakup kondisi normal, redup (gamma=1.25), silau (gamma=0.82), derau sensor (sigma=3.5), serta kemiringan pose kepala (+-2.5 derajat). Hasil eksperimen membuktikan sistem mencapai akurasi sebesar 98,00%, presisi 96,15%, recall 100,00%, F1-score 98,04%, serta False Acceptance Rate (FAR) 4,00% pada nilai ambang batas theta = 0,22. Rata-rata waktu latensi komputasi adalah 34,9 ms (~28,6 FPS) pada CPU standar, menunjukkan bahwa integrasi metode ini sangat layak diimplementasikan pada gerbang stasiun kereta api secara aman dan real-time."
    )
    doc.add_paragraph("Kata Kunci: Pengolahan Citra Digital, Face Recognition, Boarding Gate KAI, CLAHE, Local Binary Pattern Histogram, Chi-Square Distance.")

    doc.add_heading("1. PENDAHULUAN", level=1)
    doc.add_paragraph(
        "Peningkatan mobilitas masyarakat perkotaan menuntut sistem transportasi publik yang cepat, andal, dan minim hambatan antrean. Pada layanan kereta api antarkota, area pemeriksaan tiket masuk peron (boarding gate) merupakan titik kritis. Pada sistem konvensional, pemeriksaan tiket fisik atau kode QR yang dipadukan dengan pencocokan identitas KTP membutuhkan waktu 10-20 detik per penumpang, memicu antrean panjang pada jam sibuk [1]. Menjawab tantangan tersebut, otomatisasi verifikasi tiket berbasis biometrik wajah mulai diadopsi secara luas di sektor perkeretaapian untuk memfasilitasi akses peron secara contactless dalam kurun waktu kurang dari 2 detik [1], [2]."
    )
    doc.add_paragraph(
        "Tantangan nyata penerapan visi komputer di stasiun mencakup fluktuasi pencahayaan ekstrem [3], derau sensor kamera pada kondisi minim cahaya [4], serta tuntutan efisiensi komputasi edge pada prosesor CPU stasiun [2], [5]. Ekualisasi kontras adaptif lokal (CLAHE) terbukti efektif meregangkan kontras tanpa amplifikasi derau berlebih [6], [7]. Di sisi lain, Local Binary Pattern (LBP) [8] dan pengembangannya menjadi LBPH [9] mampu mengekstrak tekstur spasial mikro wajah secara invarian terhadap perubahan iluminasi monotonik. Untuk deteksi wajah awal yang cepat, cascade classifier Viola-Jones [10] tetap menjadi pilihan efisien. Makalah ini mengintegrasikan seluruh tahapan tersebut ke dalam prototipe Smart Boarding Gate KAI dengan evaluasi kuantitatif komprehensif melampaui studi pembanding lokal [11] serta menganalisis keterbatasan oklusi masker [12]."
    )

    doc.add_heading("2. METODOLOGI PENELITIAN", level=1)
    doc.add_paragraph(
        "Metodologi dirancang dengan tahapan pemrosesan citra digital sistematis: 1) Deteksi ROI wajah dengan Haar Cascade [10], 2) Penyejajaran mata (Eye Alignment) berdasarkan rotasi sudut kemiringan mata, 3) Konversi skala abu-abu luminansi standar ITU-R BT.601, 4) Penapisan derau adaptif menggunakan Bilateral Filter [4], 5) Peningkatan kontras adaptif CLAHE ubin 8x8 dan clip limit 2.5 [6], 6) Normalisasi dimensi wajah 128x128 piksel, 7) Ekstraksi fitur tekstur spasial LBPH berdimensi 16.384 [8], [9], dan 8) Klasifikasi biometrik menggunakan jarak statistik Chi-Square [9] dengan ambang batas theta = 0,22 yang terhubung langsung dengan manifest tiket basis data SQLite."
    )

    doc.add_heading("3. IMPLEMENTASI DAN HASIL PEMBAHASAN", level=1)
    doc.add_paragraph(
        "Pengujian biometrik dilakukan terhadap 50 kombinasi sampel validasi genuine dan impostor. Sistem mencapai Akurasi 98,00%, Presisi 96,15%, Recall 100,00%, F1-Score 98,04%, FAR 4,00%, dan FRR 0,00%. Hasil ini menunjukkan keunggulan signifikan dibandingkan studi pengenalan wajah LBPH sebelumnya oleh Kosasih dan Daomara [11] yang mencatatkan akurasi 86%. Ketahanan sistem terbukti stabil (100% verifikasi benar) pada seluruh simulasi gangguan redup (gamma=1.25), silau (gamma=0.82), derau sensor Gaussian (sigma=3.5), dan kemiringan kepala (+-2.5 derajat). Total waktu eksekusi adalah 34,9 ms per frame (~28,6 FPS), sejalan dengan efisiensi memori yang dilaporkan oleh Yudi et al. [5]."
    )

    doc.add_heading("4. KESIMPULAN DAN SARAN", level=1)
    doc.add_paragraph(
        "Kombinasi Bilateral Filter, CLAHE, dan LBPH terbukti sangat tangguh, berakurasi tinggi (98,00%), dan memenuhi standar pemrosesan real-time untuk gerbang peron otomatis stasiun kereta api. Pengembangan selanjutnya disarankan menambahkan modul liveness detection untuk mitigasi photo spoofing dan ekstraksi fitur mata saat terjadi oklusi masker medis [12]."
    )

    doc.add_heading("DAFTAR PUSTAKA", level=1)
    ieee_refs = [
        "[1] S. Patil, S. Trivedi, J. Jani, S. Shah, and P. Kanani, \"Digitized Railway Ticket Verification Using Facial Recognition,\" in 2021 5th International Conference on Intelligent Computing and Control Systems (ICICCS), Madurai, India, 2021, pp. 1162–1167, doi: 10.1109/ICICCS51141.2021.9432371.",
        "[2] L. Farokhah, \"Perbandingan Metode Deteksi Wajah Menggunakan OpenCV Haar Cascade, OpenCV Single Shot Multibox Detector (SSD) dan DLib CNN,\" Jurnal RESTI (Rekayasa Sistem dan Teknologi Informasi), vol. 5, no. 3, pp. 585–593, Jun. 2021, doi: 10.29207/resti.v5i3.3125.",
        "[3] P. Musa, F. A. Rafi, and M. Lamsani, \"A Review: Contrast-Limited Adaptive Histogram Equalization (CLAHE) Methods to Help the Application of Face Recognition,\" in 2018 Third International Conference on Informatics and Computing (ICIC), Palembang, Indonesia, 2018, pp. 1–6, doi: 10.1109/IAC.2018.8780492.",
        "[4] C. Tomasi and R. Manduchi, \"Bilateral Filtering for Gray and Color Images,\" in Proceedings of the Sixth IEEE International Conference on Computer Vision (ICCV), Bombay, India, 1998, pp. 839–846, doi: 10.1109/ICCV.1998.710815.",
        "[5] E. D. Yudi, Y. N. Kunang, and A. Zarkasi, \"The Memory Efficiency in a Receptionist Robot's Face Recognition System Using LBPH Algorithm,\" Jurnal RESTI (Rekayasa Sistem dan Teknologi Informasi), vol. 8, no. 6, pp. 719–729, Dec. 2024, doi: 10.29207/resti.v8i6.6048.",
        "[6] A. M. Reza, \"Realization of the Contrast Limited Adaptive Histogram Equalization (CLAHE) for Real-Time Image Enhancement,\" The Journal of VLSI Signal Processing-Systems for Signal, Image, and Video Technology, vol. 38, no. 1, pp. 35–44, Aug. 2004, doi: 10.1023/B:VLSI.0000028532.53893.82.",
        "[7] K. C. Paul and S. Aslan, \"An Improved Real-Time Face Recognition System at Low Resolution Based on Local Binary Pattern Histogram Algorithm and CLAHE,\" arXiv preprint arXiv:2104.09543, pp. 1–9, Apr. 2021.",
        "[8] T. Ojala, M. Pietikäinen, and T. Mäenpää, \"Multiresolution Gray-Scale and Rotation Invariant Texture Classification with Local Binary Patterns,\" IEEE Transactions on Pattern Analysis and Machine Intelligence, vol. 24, no. 7, pp. 971–987, Jul. 2002, doi: 10.1109/TPAMI.2002.1017623.",
        "[9] T. Ahonen, A. Hadid, and M. Pietikäinen, \"Face Description with Local Binary Patterns: Application to Face Recognition,\" IEEE Transactions on Pattern Analysis and Machine Intelligence, vol. 28, no. 12, pp. 2037–2041, Dec. 2006, doi: 10.1109/TPAMI.2006.244.",
        "[10] P. Viola and M. J. Jones, \"Robust Real-Time Face Detection,\" International Journal of Computer Vision, vol. 57, no. 2, pp. 137–154, May 2004, doi: 10.1023/B:VISI.0000013087.49260.fb.",
        "[11] R. Kosasih and C. Daomara, \"Pengenalan Wajah dengan Menggunakan Metode Local Binary Patterns Histograms (LBPH),\" Jurnal Media Informatika Budidarma, vol. 5, no. 4, pp. 1361–1367, Oct. 2021, doi: 10.30865/mib.v5i4.3217.",
        "[12] H. N. Vu, M. H. Nguyen, and C. Pham, \"Masked Face Recognition with Convolutional Neural Networks and Local Binary Patterns,\" Applied Intelligence, vol. 52, no. 5, pp. 5497–5512, Mar. 2022, doi: 10.1007/s10489-021-02728-1."
    ]
    for r in ieee_refs:
        p_ref = doc.add_paragraph(r)
        p_ref.paragraph_format.left_indent = Inches(0.4)
        p_ref.paragraph_format.first_line_indent = Inches(-0.4)

    out_file = os.path.join(DOCS_DIR, "ARTIKEL_ILMIAH.docx")
    doc.save(out_file)
    print(f"Berhasil menghasilkan: {out_file}")

def generate_slides_pptx():
    prs = pptx.Presentation()
    # 16:9 widescreen layout
    prs.slide_width = PInches(13.333)
    prs.slide_height = PInches(7.5)

    blank_layout = prs.slide_layouts[6]

    def add_header(slide, title_text, category_text="PENGOLAHAN CITRA DIGITAL"):
        # Top banner
        shape = slide.shapes.add_shape(pptx.enum.shapes.MSO_SHAPE.RECTANGLE, 0, 0, PInches(13.333), PInches(1.2))
        shape.fill.solid()
        shape.fill.fore_color.rgb = PRGBColor(0x1E, 0x2B, 0x58)
        shape.line.color.rgb = PRGBColor(0xED, 0x6B, 0x23)
        shape.line.width = PPt(4)

        txBox = slide.shapes.add_textbox(PInches(0.8), PInches(0.15), PInches(11.5), PInches(0.9))
        tf = txBox.text_frame
        p_cat = tf.paragraphs[0]
        p_cat.text = category_text.upper()
        p_cat.font.size = PPt(11)
        p_cat.font.bold = True
        p_cat.font.color.rgb = PRGBColor(0xED, 0x6B, 0x23)

        p_t = tf.add_paragraph()
        p_t.text = title_text
        p_t.font.size = PPt(22)
        p_t.font.bold = True
        p_t.font.color.rgb = PRGBColor(0xFF, 0xFF, 0xFF)

    # Slide 1: Cover
    s1 = prs.slides.add_slide(blank_layout)
    bg1 = s1.shapes.add_shape(pptx.enum.shapes.MSO_SHAPE.RECTANGLE, 0, 0, PInches(13.333), PInches(7.5))
    bg1.fill.solid()
    bg1.fill.fore_color.rgb = PRGBColor(0x1E, 0x2B, 0x58)

    tx1 = s1.shapes.add_textbox(PInches(1.0), PInches(1.5), PInches(11.3), PInches(3.0))
    tf1 = tx1.text_frame
    p1 = tf1.paragraphs[0]
    p1.text = "SMART BOARDING GATE KAI"
    p1.font.size = PPt(40)
    p1.font.bold = True
    p1.font.color.rgb = PRGBColor(0xED, 0x6B, 0x23)

    p2 = tf1.add_paragraph()
    p2.text = "Sistem Pengenalan Wajah Otomatis Berbasis CLAHE dan Local Binary Pattern Histogram (LBPH)"
    p2.font.size = PPt(20)
    p2.font.color.rgb = PRGBColor(0xFF, 0xFF, 0xFF)

    p3 = tf1.add_paragraph()
    p3.text = "\nKelompok Pengolahan Citra IF-B:\n1. Rafi Dzaka Pratama Putra (123240104)\n2. Raihan Natawangsa (123240120)\n3. Ichsan Wahyu Priambudi (123240122)\n4. Indra Naufal Firdaus (123240195)"
    p3.font.size = PPt(14)
    p3.font.color.rgb = PRGBColor(0xDC, 0xE2, 0xF0)

    # Slide 2: Latar Belakang & Alur KAI
    s2 = prs.slides.add_slide(blank_layout)
    add_header(s2, "Latar Belakang & Alur Sistem KAI")
    tx2 = s2.shapes.add_textbox(PInches(0.8), PInches(1.6), PInches(11.5), PInches(5.2))
    tf2 = tx2.text_frame
    tf2.word_wrap = True
    tf2.paragraphs[0].text = "Tantangan Nyata di Stasiun Kereta Api:"
    tf2.paragraphs[0].font.bold = True
    tf2.paragraphs[0].font.size = PPt(18)
    tf2.paragraphs[0].font.color.rgb = PRGBColor(0x1E, 0x2B, 0x58)

    bullets2 = [
        "Antrean manual pemeriksaan e-KTP dan tiket fisik membutuhkan waktu 10-20 detik per orang.",
        "KAI menerapkan Face Recognition Boarding Gate untuk mempercepat akses masuk peron secara nirsentuh.",
        "Tantangan Pengolahan Citra: Fluktuasi pencahayaan ekstrem stasiun (silau siang hari vs temaram malam), derau sensor kamera, dan kebutuhan verifikasi real-time (< 100 ms).",
        "\nAlur Operasional Resmi KAI yang Direplikasi:",
        "• Langkah 1 (Enrolment): Pendaftaran akun identitas e-KTP dan foto wajah satu kali.",
        "• Langkah 2 (Booking): Pemesanan tiket cukup NIK & Nama, otomatis terhubung dengan wajah sebelumnya (tanpa foto ulang).",
        "• Langkah 3 (Boarding): Masuk stasiun cukup menatap kamera gate, pintu peron terbuka otomatis."
    ]
    for b in bullets2:
        p = tf2.add_paragraph()
        p.text = b
        p.font.size = PPt(15)

    # Slide 3: Pipeline Pengolahan Citra
    s3 = prs.slides.add_slide(blank_layout)
    add_header(s3, "Pipeline Pengolahan Citra Digital")
    stage_img = os.path.join(EVAL_DIR, "pipeline_stages.png")
    if os.path.exists(stage_img):
        s3.shapes.add_picture(stage_img, PInches(0.8), PInches(1.8), width=PInches(11.7))

    tx3 = s3.shapes.add_textbox(PInches(0.8), PInches(4.8), PInches(11.5), PInches(2.2))
    tf3 = tx3.text_frame
    tf3.word_wrap = True
    bullets3 = [
        "1. Deteksi Wajah & Eye Alignment: Isolasi ROI dan rotasi afin bila kepala miring agar sepasang mata sejajar horizontal.",
        "2. Konversi Grayscale (ITU-R BT.601): Mereduksi volume dimensi warna dari 3 kanal menjadi 1 kanal luminansi.",
        "3. Bilateral Filter: Menghaluskan derau sensor seragam tanpa mengaburkan tepi kontur mata dan bibir.",
        "4. CLAHE (Contrast Limited Adaptive Histogram Equalization): Normalisasi kontras lokal pada ubin 8x8 guna menekan efek silau.",
        "5. Ekstraksi LBPH: Grid 8x8 sel, menghasilkan 16.384 dimensi ciri tekstur mikro spasial."
    ]
    for idx, b in enumerate(bullets3):
        p = tf3.paragraphs[0] if idx == 0 else tf3.add_paragraph()
        p.text = b
        p.font.size = PPt(14)

    # Slide 4: Evaluasi & Metrik
    s4 = prs.slides.add_slide(blank_layout)
    add_header(s4, "Hasil Pengujian & Evaluasi Kinerja (Bagian 9)")

    cm_img = os.path.join(EVAL_DIR, "confusion_matrix.png")
    if os.path.exists(cm_img):
        s4.shapes.add_picture(cm_img, PInches(0.8), PInches(1.8), width=PInches(4.5))

    curve_img = os.path.join(EVAL_DIR, "far_frr_curve.png")
    if os.path.exists(curve_img):
        s4.shapes.add_picture(curve_img, PInches(5.6), PInches(1.8), width=PInches(5.5))

    tx4 = s4.shapes.add_textbox(PInches(0.8), PInches(5.8), PInches(11.5), PInches(1.4))
    tf4 = tx4.text_frame
    p4 = tf4.paragraphs[0]
    p4.text = "Hasil Kuantitatif: Akurasi = 98.00% | Presisi = 96.15% | Recall = 100.00% | F1-Score = 98.04% | FAR = 4.00% | FRR = 0.00% | Latensi = 34.9 ms (~28.6 FPS)"
    p4.font.bold = True
    p4.font.size = PPt(14)
    p4.font.color.rgb = PRGBColor(0x1B, 0x5E, 0x20)

    # Slide 5: Kesimpulan
    s5 = prs.slides.add_slide(blank_layout)
    add_header(s5, "Kesimpulan & Pembagian Kerja")
    tx5 = s5.shapes.add_textbox(PInches(0.8), PInches(1.6), PInches(11.5), PInches(5.2))
    tf5 = tx5.text_frame
    tf5.word_wrap = True
    bullets5 = [
        "Kesimpulan Akhir:",
        "• Sistem berhasil mengintegrasikan metode pengolahan citra digital klasik (Bilateral Filter, CLAHE, LBPH) dengan logika bisnis boarding gate KAI.",
        "• Waktu pemrosesan 34,9 ms (~28,6 FPS) membuktikan efisiensi komputasi tinggi pada CPU standar tanpa perlu GPU eksternal.",
        "• Sistem mampu mencegah akses tiket ganda (ALREADY_BOARDED) dan menolak tiket yang tanggalnya salah (WRONG_DATE).",
        "\nPembagian Peran Anggota Kelompok:",
        "• Rafi Dzaka Pratama Putra: Database, Logika Tiket KAI, & Integrasi Sistem",
        "• Raihan Natawangsa: Frontend Web Streamlit & Visualisasi UI/UX",
        "• Ichsan Wahyu Priambudi: Deteksi Wajah, Eye Alignment, CLAHE, & Ekstraksi LBPH",
        "• Indra Naufal Firdaus: Dataset Wajah Nyata, Evaluasi Metrik, & Benchmarking"
    ]
    for idx, b in enumerate(bullets5):
        p = tf5.paragraphs[0] if idx == 0 else tf5.add_paragraph()
        p.text = b
        p.font.size = PPt(15)

    out_file = os.path.join(DOCS_DIR, "SLIDE_PRESENTASI.pptx")
    prs.save(out_file)
    print(f"Berhasil menghasilkan: {out_file}")

if __name__ == "__main__":
    generate_laporan_docx()
    generate_artikel_docx()
    generate_slides_pptx()
