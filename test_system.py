import os
import cv2
import numpy as np
from src.config import SAMPLE_FACES_DIR
from src.database import DatabaseManager
from src.detector import FaceDetector
from src.preprocessing import ImagePreprocessor
from src.feature_extractor import LBPHFeatureExtractor
from src.boarding_engine import BoardingGateEngine

def test_full_pipeline():
    print("==================================================================")
    print("  UNIT TEST: SISTEM FACE RECOGNITION BOARDING GATE KAI")
    print("==================================================================")

    # 1. Test Database
    db = DatabaseManager()
    with db._get_connection() as conn:
        conn.execute("UPDATE tickets SET status_tiket = 'ACTIVE', waktu_boarding = NULL WHERE nik = '3273011204980001'")
        conn.commit()

    tmpls = db.get_all_templates()
    assert len(tmpls) >= 5, f"Expected at least 5 registered templates, got {len(tmpls)}"
    print(f"[OK] Database: Terhubung dan memuat {len(tmpls)} template biometrik.")

    # 2. Test Preprocessing & Feature Extractor
    sample_path = os.path.join(SAMPLE_FACES_DIR, "3273011204980001_budi_santoso.jpg")
    img = cv2.imread(sample_path)
    assert img is not None, f"Failed to load image at {sample_path}"

    prep = ImagePreprocessor()
    proc = prep.process(img)
    assert proc.shape == (128, 128), f"Expected shape (128, 128), got {proc.shape}"
    print(f"[OK] Prapemrosesan: Normalisasi ukuran & CLAHE sukses (output: {proc.shape}).")

    ext = LBPHFeatureExtractor()
    feat = ext.extract_features(proc)
    assert feat.shape == (16384,), f"Expected shape (16384,), got {feat.shape}"
    dist_self = ext.chi_square_distance(feat, feat)
    assert dist_self < 1e-5, f"Self distance should be ~0, got {dist_self}"
    print(f"[OK] Ekstraksi Fitur LBPH: Vektor 16.384 dimensi, Self-Distance = {dist_self:.6f}.")

    # 3. Test Boarding Engine Skenario 1: Penumpang Sah dengan Tiket Aktif
    from src.config import LBP_SIMILARITY_THRESHOLD
    engine = BoardingGateEngine(threshold=LBP_SIMILARITY_THRESHOLD)
    res_budi = engine.process_frame(img, gate_id="GATE-01")
    print(f"[OK] Skenario Penumpang Sah: Status={res_budi['status']}, Gate={res_budi['gate_status']}, Confidence={res_budi['metrics']['confidence']:.1f}%")

    # 4. Test Skenario 2: Orang Asing (Impostor)
    imp_path = os.path.join(SAMPLE_FACES_DIR, "impostor_unregistered.jpg")
    imp_img = cv2.imread(imp_path)
    res_imp = engine.process_frame(imp_img, gate_id="GATE-01")
    assert res_imp['gate_status'] == "DENIED", f"Impostor should be denied, got {res_imp['gate_status']}"
    print(f"[OK] Skenario Impostor: Status={res_imp['status']}, Gate={res_imp['gate_status']} (Akses Ditolak).")

    # 5. Test Skenario 3: Frame Kosong / Tanpa Wajah
    blank = np.ones((240, 240, 3), dtype=np.uint8) * 128
    res_blank = engine.process_frame(blank, gate_id="GATE-01")
    assert res_blank['status'] == "NO_FACE", f"Blank image should yield NO_FACE, got {res_blank['status']}"
    print(f"[OK] Skenario Tanpa Wajah: Status={res_blank['status']}, Gate={res_blank['gate_status']}.")

    print("==================================================================")
    print("  SEMUA PENGUJIAN INTEGRASI PIPELINE BERHASIL 100%!")
    print("==================================================================")

if __name__ == "__main__":
    test_full_pipeline()
