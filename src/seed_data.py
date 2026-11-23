import os
import cv2
import numpy as np
from src.config import SAMPLE_FACES_DIR
from src.database import DatabaseManager
from src.detector import FaceDetector
from src.preprocessing import ImagePreprocessor
from src.feature_extractor import LBPHFeatureExtractor

def generate_procedural_face(
    seed: int,
    skin_tone: tuple = (200, 220, 240),
    hair_style: str = "short",
    eye_offset_y: int = 0,
    mouth_type: str = "smile",
    has_glasses: bool = False,
    has_mustache: bool = False,
    is_hijab: bool = False
) -> np.ndarray:
    """
    Membuat citra wajah sintetis dengan variasi tekstur dan struktur anatomi
    yang kaya (rambut, hijab, kumis, kacamata, bentuk rahang) agar menghasilkan
    deskriptor tekstur LBPH yang sangat diskriminatif dan khas per individu.
    """
    np.random.seed(seed)
    w, h = 240, 240
    img = np.ones((h, w, 3), dtype=np.uint8) * 242

    center = (w // 2, h // 2 + 10)
    axes = (68 + (seed % 11), 88 + (seed % 9))

    # 1. Leher dan Bahu
    cv2.rectangle(img, (center[0] - 35, center[1] + axes[1] - 15), (center[0] + 35, h), skin_tone, -1)
    cv2.ellipse(img, (center[0], h + 30), (105, 55), 0, 0, 360, (50 + (seed*15)%100, 70, 110), -1, cv2.LINE_AA)

    # 2. Kontur Kepala / Rahang
    cv2.ellipse(img, center, axes, 0, 0, 360, skin_tone, -1, cv2.LINE_AA)
    border_color = (max(0, skin_tone[0]-45), max(0, skin_tone[1]-45), max(0, skin_tone[2]-45))
    cv2.ellipse(img, center, axes, 0, 0, 360, border_color, 2, cv2.LINE_AA)

    # 3. Rambut atau Hijab
    hair_color = (25 + (seed % 20), 20 + (seed % 15), 18)
    hair_top = center[1] - axes[1]

    if is_hijab:
        hijab_color = (70 + (seed*20)%80, 85 + (seed*15)%80, 130 + (seed*10)%80)
        # Bentuk luar kerudung / hijab
        cv2.ellipse(img, (center[0], center[1] - 5), (axes[0] + 18, axes[1] + 28), 0, 0, 360, hijab_color, -1, cv2.LINE_AA)
        # Lingkar wajah dalam hijab
        cv2.ellipse(img, (center[0], center[1] + 8), (axes[0] - 6, axes[1] - 10), 0, 0, 360, skin_tone, -1, cv2.LINE_AA)
        cv2.ellipse(img, (center[0], center[1] + 8), (axes[0] - 6, axes[1] - 10), 0, 0, 360, border_color, 2, cv2.LINE_AA)
    else:
        if hair_style == "short":
            cv2.ellipse(img, (center[0], hair_top + 28), (axes[0] + 8, 48), 0, 180, 360, hair_color, -1, cv2.LINE_AA)
            cv2.rectangle(img, (center[0] - axes[0] - 6, hair_top + 15), (center[0] - axes[0] + 8, center[1] - 10), hair_color, -1)
            cv2.rectangle(img, (center[0] + axes[0] - 8, hair_top + 15), (center[0] + axes[0] + 6, center[1] - 10), hair_color, -1)
        elif hair_style == "parted":
            cv2.ellipse(img, (center[0] - 10, hair_top + 26), (axes[0] + 6, 45), -10, 170, 360, hair_color, -1, cv2.LINE_AA)
            cv2.ellipse(img, (center[0] + 20, hair_top + 24), (axes[0] - 10, 40), 15, 180, 350, hair_color, -1, cv2.LINE_AA)
        elif hair_style == "curly":
            for cx_offset in range(-axes[0], axes[0] + 1, 18):
                cv2.circle(img, (center[0] + cx_offset, hair_top + 20), 16, hair_color, -1, cv2.LINE_AA)
        elif hair_style == "long":
            cv2.ellipse(img, (center[0], hair_top + 28), (axes[0] + 8, 50), 0, 180, 360, hair_color, -1, cv2.LINE_AA)
            cv2.rectangle(img, (center[0] - axes[0] - 12, hair_top + 20), (center[0] - axes[0] + 6, center[1] + 50), hair_color, -1)
            cv2.rectangle(img, (center[0] + axes[0] - 6, hair_top + 20), (center[0] + axes[0] + 12, center[1] + 50), hair_color, -1)

    # 4. Telinga
    if not is_hijab:
        cv2.ellipse(img, (center[0] - axes[0] - 2, center[1] - 2), (10, 18), 0, 0, 360, skin_tone, -1, cv2.LINE_AA)
        cv2.ellipse(img, (center[0] + axes[0] + 2, center[1] - 2), (10, 18), 0, 0, 360, skin_tone, -1, cv2.LINE_AA)

    # 5. Alis Mata
    brow_y = center[1] - 32 + eye_offset_y
    brow_color = (25, 20, 15)
    cv2.line(img, (center[0] - 46, brow_y), (center[0] - 16, brow_y - 4), brow_color, 4, cv2.LINE_AA)
    cv2.line(img, (center[0] + 16, brow_y - 4), (center[0] + 46, brow_y), brow_color, 4, cv2.LINE_AA)

    # 6. Mata & Pupil
    eye_y = center[1] - 16 + eye_offset_y
    for eye_x in [center[0] - 31, center[0] + 31]:
        cv2.ellipse(img, (eye_x, eye_y), (14, 8), 0, 0, 360, (255, 255, 255), -1, cv2.LINE_AA)
        cv2.circle(img, (eye_x, eye_y), 5, (45, 30, 15), -1, cv2.LINE_AA)
        cv2.circle(img, (eye_x - 1, eye_y - 1), 2, (255, 255, 255), -1, cv2.LINE_AA)
        cv2.ellipse(img, (eye_x, eye_y), (14, 8), 0, 0, 360, border_color, 1, cv2.LINE_AA)

    # 7. Kacamata
    if has_glasses:
        gc = (35, 35, 35)
        cv2.rectangle(img, (center[0] - 50, eye_y - 15), (center[0] - 12, eye_y + 13), gc, 3, cv2.LINE_AA)
        cv2.rectangle(img, (center[0] + 12, eye_y - 15), (center[0] + 50, eye_y + 13), gc, 3, cv2.LINE_AA)
        cv2.line(img, (center[0] - 12, eye_y - 1), (center[0] + 12, eye_y - 1), gc, 3, cv2.LINE_AA)

    # 8. Hidung
    nose_y = center[1] + 16
    cv2.line(img, (center[0], eye_y + 6), (center[0] - 4, nose_y), border_color, 2, cv2.LINE_AA)
    cv2.line(img, (center[0] - 4, nose_y), (center[0] + 7, nose_y), border_color, 2, cv2.LINE_AA)

    # 9. Kumis
    if has_mustache:
        cv2.ellipse(img, (center[0], nose_y + 14), (24, 7), 0, 0, 180, (25, 20, 15), -1, cv2.LINE_AA)

    # 10. Mulut & Bibir
    mouth_y = center[1] + 52
    lip_color = (80, 70, 175)
    if mouth_type == "smile":
        cv2.ellipse(img, (center[0], mouth_y - 8), (25, 15), 0, 15, 165, lip_color, 3, cv2.LINE_AA)
    else:
        cv2.line(img, (center[0] - 22, mouth_y), (center[0] + 22, mouth_y), lip_color, 3, cv2.LINE_AA)

    # Gaussian noise halus untuk realisme sensor kamera
    noise = np.random.normal(0, 3, img.shape).astype(np.int16)
    img = np.clip(img.astype(np.int16) + noise, 0, 255).astype(np.uint8)

    return img

def seed_database():
    """Menginisialisasi basis data dengan manifest penumpang KAI realistis."""
    db = DatabaseManager()
    detector = FaceDetector()
    preprocessor = ImagePreprocessor()
    extractor = LBPHFeatureExtractor()
    os.makedirs(SAMPLE_FACES_DIR, exist_ok=True)

    passengers_data = [
        {
            "nik": "3273011204980001",
            "nama": "Budi Santoso",
            "gender": "Laki-laki",
            "telepon": "081234567801",
            "skin": (175, 205, 230),
            "hair_style": "short",
            "mouth": "smile",
            "glasses": False,
            "mustache": False,
            "is_hijab": False,
            "seed": 101,
            "ticket": {
                "code": "KAI-7G4B9X",
                "kereta": "Argo Parahyangan (KA 35)",
                "relasi": "Gambir (GMR) - Bandung (BD)",
                "jadwal": "2026-11-24 08:30:00",
                "kursi": "Eksekutif 2 / 12A",
                "status": "ACTIVE"
            }
        },
        {
            "nik": "3171054308990002",
            "nama": "Siti Aminah",
            "gender": "Perempuan",
            "telepon": "081234567802",
            "skin": (195, 225, 245),
            "hair_style": "short",
            "mouth": "smile",
            "glasses": True,
            "mustache": False,
            "is_hijab": True,
            "seed": 202,
            "ticket": {
                "code": "KAI-3M9K2L",
                "kereta": "Taksaka (KA 68)",
                "relasi": "Gambir (GMR) - Yogyakarta (YK)",
                "jadwal": "2026-11-24 09:15:00",
                "kursi": "Eksekutif 1 / 4D",
                "status": "ACTIVE"
            }
        },
        {
            "nik": "3578021509950003",
            "nama": "Ahmad Pratama",
            "gender": "Laki-laki",
            "telepon": "081234567803",
            "skin": (160, 195, 220),
            "hair_style": "curly",
            "mouth": "neutral",
            "glasses": False,
            "mustache": True,
            "is_hijab": False,
            "seed": 303,
            "ticket": {
                "code": "KAI-8V2P4Q",
                "kereta": "Argo Bromo Anggrek (KA 2)",
                "relasi": "Gambir (GMR) - Surabaya Pasarturi (SBI)",
                "jadwal": "2026-11-24 07:00:00",
                "kursi": "Luxury 1 / 2A",
                "status": "BOARDED"
            }
        },
        {
            "nik": "3374016601010004",
            "nama": "Dewi Lestari",
            "gender": "Perempuan",
            "telepon": "081234567804",
            "skin": (205, 230, 248),
            "hair_style": "long",
            "mouth": "smile",
            "glasses": False,
            "mustache": False,
            "is_hijab": False,
            "seed": 404,
            "ticket": {
                "code": "KAI-5T7H1Y",
                "kereta": "Lodaya (KA 92)",
                "relasi": "Bandung (BD) - Solo Balapan (SLO)",
                "jadwal": "2026-11-24 10:00:00",
                "kursi": "Eksekutif 3 / 8B",
                "status": "ACTIVE"
            }
        },
        {
            "nik": "3271032805970005",
            "nama": "Rian Kurniawan",
            "gender": "Laki-laki",
            "telepon": "081234567805",
            "skin": (170, 200, 228),
            "hair_style": "parted",
            "mouth": "neutral",
            "glasses": True,
            "mustache": False,
            "is_hijab": False,
            "seed": 505,
            "ticket": None
        }
    ]

    print("Menginisialisasi basis data penumpang dan menghasilkan data citra wajah...")

    for p in passengers_data:
        face_img = generate_procedural_face(
            seed=p["seed"],
            skin_tone=p["skin"],
            hair_style=p["hair_style"],
            mouth_type=p["mouth"],
            has_glasses=p["glasses"],
            has_mustache=p["mustache"],
            is_hijab=p["is_hijab"]
        )
        img_filename = f"{p['nik']}_{p['nama'].replace(' ', '_').lower()}.jpg"
        img_path = os.path.join(SAMPLE_FACES_DIR, img_filename)
        cv2.imwrite(img_path, face_img)

        db.save_passenger(
            nik=p["nik"],
            nama=p["nama"],
            jenis_kelamin=p["gender"],
            telepon=p["telepon"],
            foto_path=img_path
        )

        # Deteksi ROI wajah agar geometri prapemrosesan identik dengan sensor boarding gate
        _, face_roi = detector.detect_primary_face(face_img)
        if face_roi is None:
            face_roi = face_img

        prep_face = preprocessor.process(face_roi)
        features = extractor.extract_features(prep_face)
        db.save_face_template(nik=p["nik"], method="LBPH", feature_vector=features)

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

    # Buat orang asing (impostor)
    impostor_img = generate_procedural_face(
        seed=999,
        skin_tone=(140, 170, 205),
        hair_style="curly",
        mouth_type="neutral",
        has_glasses=False,
        has_mustache=True,
        is_hijab=False
    )
    cv2.imwrite(os.path.join(SAMPLE_FACES_DIR, "impostor_unregistered.jpg"), impostor_img)

    print(f"Berhasil menginisialisasi {len(passengers_data)} data penumpang dan impostor.")

if __name__ == "__main__":
    seed_database()
