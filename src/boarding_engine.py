import numpy as np
import cv2
from typing import Dict, Any, Optional
from datetime import datetime
from src.config import LBP_SIMILARITY_THRESHOLD
from src.detector import FaceDetector
from src.preprocessing import ImagePreprocessor
from src.feature_extractor import LBPHFeatureExtractor
from src.database import DatabaseManager

class BoardingGateEngine:
    """
    Mesin Utama Boarding Gate KAI berbasis Pengenalan Wajah Otomatis (Face Recognition).
    Mengintegrasikan deteksi, prapemrosesan, ekstraksi ciri LBPH, pencocokan biometrik 1:N,
    serta verifikasi aturan bisnis tiket KAI secara real-time.
    """

    def __init__(self, threshold: float = LBP_SIMILARITY_THRESHOLD):
        self.threshold = threshold
        self.detector = FaceDetector()
        self.preprocessor = ImagePreprocessor()
        self.feature_extractor = LBPHFeatureExtractor()
        self.db = DatabaseManager()

    def set_threshold(self, new_threshold: float):
        """Memperbarui nilai ambang batas sensitivitas kecocokan (tuning threshold)."""
        self.threshold = new_threshold

    def process_frame(self, frame_bgr: np.ndarray, gate_id: str = "GATE-01") -> Dict[str, Any]:
        """
        Memproses satu frame citra dari kamera gate.
        Menghasilkan status boarding, data penumpang, dan visualisasi citra.
        """
        start_time = datetime.now()

        # 1. Tahap Deteksi Wajah
        bbox, face_roi = self.detector.detect_primary_face(frame_bgr)
        if bbox is None or face_roi is None:
            annotated_frame = self.detector.draw_gate_hud(
                frame_bgr, bbox=None, status_text="ARAHKAN WAJAH KE KAMERA", is_success=None
            )
            return {
                "status": "NO_FACE",
                "gate_status": "WAITING",
                "message": "Silakan berdiri di depan kamera gate dan hadap lurus.",
                "annotated_frame": annotated_frame,
                "passenger": None,
                "ticket": None,
                "metrics": {"latency_ms": 0.0, "distance": 1.0, "confidence": 0.0},
                "stages": None
            }

        # 2. Tahap Prapemrosesan Citra
        preprocessed_face = self.preprocessor.process(face_roi)
        stages = self.preprocessor.get_intermediate_stages(face_roi)

        # 3. Ekstraksi Fitur Tekstur Spasial (LBPH)
        query_vector = self.feature_extractor.extract_features(preprocessed_face)

        # Tambahkan citra LBP ke visualisasi tahapan
        lbp_map = self.feature_extractor.compute_lbp_image(preprocessed_face)
        stages["7. Peta Tekstur Spasial (LBP 2D)"] = lbp_map

        # 4. Pencocokan Biometrik 1:N (Identifikasi Terhadap Basis Data Penumpang)
        templates = self.db.get_all_templates(method="LBPH")
        best_match = None
        min_distance = float("inf")

        for tmpl in templates:
            dist = self.feature_extractor.chi_square_distance(query_vector, tmpl["feature_vector"])
            if dist < min_distance:
                min_distance = dist
                best_match = tmpl

        # Kalkulasi estimasi confidence score (%) berdasarkan rasio threshold
        # Semakin kecil Chi-Square distance, semakin identik (confidence mendekati 100%)
        if min_distance < self.threshold:
            confidence = max(0.0, min(100.0, (1.0 - (min_distance / (self.threshold * 1.5))) * 100.0))
            is_recognized = True
        else:
            confidence = max(0.0, min(60.0, (1.0 - (min_distance / 1.0)) * 50.0)) if min_distance < 1.0 else 0.0
            is_recognized = False

        # Hitung latensi waktu komputasi pemrosesan frame (milidetik)
        elapsed_ms = (datetime.now() - start_time).total_seconds() * 1000.0

        # 5. Verifikasi Tiket Kereta dan Eksekusi Aturan Bisnis Boarding KAI
        if not is_recognized or best_match is None:
            # Wajah tidak dikenali dalam database penumpang terdaftar
            self.db.log_gate_event(
                gate_id=gate_id,
                status="UNRECOGNIZED",
                pesan="Wajah tidak dikenali atau belum terdaftar dalam sistem KAI Face Recognition.",
                confidence=confidence,
                distance=min_distance
            )
            annotated_frame = self.detector.draw_gate_hud(
                frame_bgr, bbox=bbox, status_text="TIDAK TERDAFTAR", is_success=False
            )
            return {
                "status": "UNRECOGNIZED",
                "gate_status": "DENIED",
                "message": "Wajah Anda belum terdaftar di KAI Access Face Recognition. Silakan gunakan tiket manual atau scan barcode tiket.",
                "annotated_frame": annotated_frame,
                "passenger": None,
                "ticket": None,
                "metrics": {"latency_ms": elapsed_ms, "distance": min_distance, "confidence": confidence},
                "stages": stages
            }

        # Penumpang Dikenali
        nik = best_match["nik"]
        passenger_name = best_match["nama"]
        passenger_info = self.db.get_passenger(nik)
        active_ticket = self.db.get_active_ticket_for_passenger(nik)

        if not active_ticket:
            # Penumpang terdaftar tetapi tidak memiliki manifest tiket untuk hari ini
            self.db.log_gate_event(
                gate_id=gate_id,
                nik=nik,
                nama=passenger_name,
                status="NO_TICKET",
                pesan="Penumpang terdaftar, namun tidak memiliki tiket perjalanan aktif.",
                confidence=confidence,
                distance=min_distance
            )
            annotated_frame = self.detector.draw_gate_hud(
                frame_bgr, bbox=bbox, status_text="TIKET TIDAK DITEMUKAN", is_success=False, passenger_name=passenger_name
            )
            return {
                "status": "NO_TICKET",
                "gate_status": "DENIED",
                "message": f"Halo {passenger_name}, Anda tidak memiliki jadwal tiket aktif pada stasiun keberangkatan ini.",
                "annotated_frame": annotated_frame,
                "passenger": passenger_info,
                "ticket": None,
                "metrics": {"latency_ms": elapsed_ms, "distance": min_distance, "confidence": confidence},
                "stages": stages
            }

        ticket_code = active_ticket["ticket_code"]
        ticket_status = active_ticket["status_tiket"]

        if ticket_status == "BOARDED":
            # Tiket sudah pernah dipindai / boarding sebelumnya (mencegah double-entry / pass-back)
            self.db.log_gate_event(
                gate_id=gate_id,
                nik=nik,
                nama=passenger_name,
                ticket_code=ticket_code,
                status="ALREADY_BOARDED",
                pesan=f"Tiket {ticket_code} telah digunakan sebelumnya pada {active_ticket['waktu_boarding']}.",
                confidence=confidence,
                distance=min_distance
            )
            annotated_frame = self.detector.draw_gate_hud(
                frame_bgr, bbox=bbox, status_text="SUDAH BOARDING", is_success=False, passenger_name=passenger_name
            )
            return {
                "status": "ALREADY_BOARDED",
                "gate_status": "DENIED",
                "message": f"Tiket {ticket_code} atas nama {passenger_name} sudah digunakan pada {active_ticket.get('waktu_boarding', '-')}.",
                "annotated_frame": annotated_frame,
                "passenger": passenger_info,
                "ticket": active_ticket,
                "metrics": {"latency_ms": elapsed_ms, "distance": min_distance, "confidence": confidence},
                "stages": stages
            }

        # Boarding Sukses: Wajah cocok & Tiket Aktif!
        self.db.mark_ticket_boarded(ticket_code)
        self.db.log_gate_event(
            gate_id=gate_id,
            nik=nik,
            nama=passenger_name,
            ticket_code=ticket_code,
            status="SUCCESS",
            pesan=f"Verifikasi Berhasil! Selamat Menikmati Perjalanan dengan {active_ticket['nama_kereta']}.",
            confidence=confidence,
            distance=min_distance
        )

        annotated_frame = self.detector.draw_gate_hud(
            frame_bgr, bbox=bbox, status_text="VERIFIED - SILAKAN MASUK", is_success=True, passenger_name=passenger_name
        )

        return {
            "status": "SUCCESS",
            "gate_status": "GRANTED",
            "message": f"Verifikasi Berhasil! Selamat datang, {passenger_name}. Silakan menuju peron keberangkatan {active_ticket['nama_kereta']}.",
            "annotated_frame": annotated_frame,
            "passenger": passenger_info,
            "ticket": active_ticket,
            "metrics": {"latency_ms": elapsed_ms, "distance": min_distance, "confidence": confidence},
            "stages": stages
        }
