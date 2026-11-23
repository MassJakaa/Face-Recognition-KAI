import os
import cv2
import sys
from src.config import SAMPLE_FACES_DIR, LBP_SIMILARITY_THRESHOLD
from src.database import DatabaseManager
from src.boarding_engine import BoardingGateEngine

def run_cli_demo():
    print("==================================================================")
    print("  SIMULASI SMART BOARDING GATE KAI - FACE RECOGNITION (CLI MODE)")
    print("==================================================================")

    # Reset status tiket untuk demonstrasi
    db = DatabaseManager()
    with db._get_connection() as conn:
        conn.execute("UPDATE tickets SET status_tiket = 'ACTIVE', waktu_boarding = NULL WHERE nik != '3578021509950003'")
        conn.commit()

    engine = BoardingGateEngine(threshold=LBP_SIMILARITY_THRESHOLD)
    sample_files = [f for f in os.listdir(SAMPLE_FACES_DIR) if f.endswith(".jpg")]

    print("\nDaftar Citra Sampel Penumpang Tersedia:")
    for i, fname in enumerate(sample_files, 1):
        print(f"  [{i}] {fname}")

    print("\nMenjalankan Pengujian Otomatis pada Semua Sampel...")
    print("-" * 75)
    print(f"{'File Sampel':<35} | {'Status':<15} | {'Gate Status':<10} | {'Confidence':<10}")
    print("-" * 75)

    for fname in sample_files:
        fpath = os.path.join(SAMPLE_FACES_DIR, fname)
        img = cv2.imread(fpath)
        if img is None:
            continue

        res = engine.process_frame(img, gate_id="GATE-01")
        status = res["status"]
        gate_status = res["gate_status"]
        conf = f"{res['metrics']['confidence']:.1f}%"
        print(f"{fname:<35} | {status:<15} | {gate_status:<10} | {conf:<10}")

    print("-" * 75)
    print("\nUntuk menjalankan antarmuka grafis interaktif (Web UI), ketik:")
    print("  streamlit run app.py\n")

if __name__ == "__main__":
    run_cli_demo()
