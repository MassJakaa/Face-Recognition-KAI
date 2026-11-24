import os
import cv2
import numpy as np
from datetime import datetime
from src.config import SAMPLE_FACES_DIR
from src.database import DatabaseManager
from src.detector import FaceDetector
from src.preprocessing import ImagePreprocessor
from src.feature_extractor import LBPHFeatureExtractor

def seed_database():
    """
    Menginisialisasi basis data menggunakan foto wajah manusia asli (real human passport photos)
    untuk 5 penumpang resmi KAI dan 1 data orang asing (impostor).
    """
    db = DatabaseManager()
    detector = FaceDetector()
    preprocessor = ImagePreprocessor()
    extractor = LBPHFeatureExtractor()
    os.makedirs(SAMPLE_FACES_DIR, exist_ok=True)

    today_str = datetime.now().strftime("%Y-%m-%d")

    passengers_data = [
        {
            "nik": "3273011204980001",
            "nama": "Budi Santoso",
            "gender": "Laki-laki",
            "telepon": "081234567801",
            "filename": "3273011204980001_budi_santoso.jpg",
            "ticket": {
                "code": "KAI-7G4B9X",
                "kereta": "Argo Parahyangan (KA 35)",
                "relasi": "Gambir (GMR) - Bandung (BD)",
                "jadwal": f"{today_str} 08:30:00",
                "kursi": "Eksekutif 2 / 12A",
                "status": "ACTIVE"
            }
        },
        {
            "nik": "3171054308990002",
            "nama": "Siti Aminah",
            "gender": "Perempuan",
            "telepon": "081234567802",
            "filename": "3171054308990002_siti_aminah.jpg",
            "ticket": {
                "code": "KAI-3M9K2L",
                "kereta": "Taksaka (KA 68)",
                "relasi": "Gambir (GMR) - Yogyakarta (YK)",
                "jadwal": f"{today_str} 09:15:00",
                "kursi": "Eksekutif 1 / 4D",
                "status": "ACTIVE"
            }
        },
        {
            "nik": "3578021509950003",
            "nama": "Ahmad Pratama",
            "gender": "Laki-laki",
            "telepon": "081234567803",
            "filename": "3578021509950003_ahmad_pratama.jpg",
            "ticket": {
                "code": "KAI-8V2P4Q",
                "kereta": "Argo Bromo Anggrek (KA 2)",
                "relasi": "Gambir (GMR) - Surabaya Pasarturi (SBI)",
                "jadwal": f"{today_str} 07:00:00",
                "kursi": "Luxury 1 / 2A",
                "status": "BOARDED"  # Tiket sudah pernah dipakai (uji kondisi gagal)
            }
        },
        {
            "nik": "3374016601010004",
            "nama": "Dewi Lestari",
            "gender": "Perempuan",
            "telepon": "081234567804",
            "filename": "3374016601010004_dewi_lestari.jpg",
            "ticket": {
                "code": "KAI-5T7H1Y",
                "kereta": "Lodaya (KA 92)",
                "relasi": "Bandung (BD) - Solo Balapan (SLO)",
                "jadwal": f"{today_str} 10:00:00",
                "kursi": "Eksekutif 3 / 8B",
                "status": "ACTIVE"
            }
        },
        {
            "nik": "3271032805970005",
            "nama": "Rian Kurniawan",
            "gender": "Laki-laki",
            "telepon": "081234567805",
            "filename": "3271032805970005_rian_kurniawan.jpg",
            "ticket": None  # Penumpang terdaftar tapi tidak punya tiket aktif
        }
    ]

    print("Menginisialisasi basis data menggunakan citra foto manusia asli...")

    for p in passengers_data:
        img_path = os.path.join(SAMPLE_FACES_DIR, p["filename"])
        if not os.path.exists(img_path):
            print(f"Warning: File {img_path} tidak ditemukan!")
            continue

        face_img = cv2.imread(img_path)

        # Simpan data penumpang ke basis data
        db.save_passenger(
            nik=p["nik"],
            nama=p["nama"],
            jenis_kelamin=p["gender"],
            telepon=p["telepon"],
            foto_path=img_path
        )

        # Deteksi ROI wajah dan lakukan prapemrosesan (Grayscale, Bilateral, CLAHE, Resize)
        _, face_roi = detector.detect_primary_face(face_img)
        if face_roi is None:
            face_roi = face_img

        prep_face = preprocessor.process(face_roi)
        features = extractor.extract_features(prep_face)
        db.save_face_template(nik=p["nik"], method="LBPH", feature_vector=features)

        # Simpan manifest tiket jika ada
        if p["ticket"]:
            t = p["ticket"]
            db.save_ticket(
                ticket_code=t["code"],
                nik=p["nik"],
                nama_kereta=t["kereta"],
                relasi=t["relasi"],
                jadwal_berangkat=t["jadwal"],
                gerbong_kursi=t["kursi"],
                status_tiket=t["status"]
            )
            if t["status"] == "BOARDED":
                db.mark_ticket_boarded(t["code"])

    print(f"Sukses menginisialisasi {len(passengers_data)} data penumpang dengan foto manusia asli.")

if __name__ == "__main__":
    seed_database()
