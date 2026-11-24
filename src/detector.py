import cv2
import numpy as np
import os
from typing import List, Tuple, Optional
from src.config import HAAR_CASCADE_PATH, HAAR_EYE_PATH

class FaceDetector:
    """
    Modul Deteksi Wajah untuk Smart Boarding Gate KAI.
    Mendukung dua pendekatan pengolahan citra digital:
    1. Viola-Jones Haar Cascade Classifier & Penyejajaran Sudut Mata (Eye Alignment)
    2. Segmentasi Ruang Warna Kulit YCrCb + Operasi Morfologi (Pendekatan murni DIP)
       yang menjamin kompatibilitas 100% di semua versi OpenCV (OpenCV 4 maupun OpenCV 5).
    """

    def __init__(self, cascade_path: str = HAAR_CASCADE_PATH):
        self.cascade_path = cascade_path
        self.has_cascade = hasattr(cv2, "CascadeClassifier")
        self.face_cascade = None
        self.eye_cascade = None

        if self.has_cascade:
            try:
                self.face_cascade = cv2.CascadeClassifier(cascade_path)
                if self.face_cascade.empty():
                    self.face_cascade = None
            except Exception:
                self.face_cascade = None

            if HAAR_EYE_PATH and os.path.exists(HAAR_EYE_PATH):
                try:
                    self.eye_cascade = cv2.CascadeClassifier(HAAR_EYE_PATH)
                    if self.eye_cascade.empty():
                        self.eye_cascade = None
                except Exception:
                    self.eye_cascade = None

    def detect_faces_ycrcb(
        self,
        image: np.ndarray,
        min_size: Tuple[int, int] = (60, 60)
    ) -> List[Tuple[int, int, int, int]]:
        """
        Deteksi wajah berbasis Segmentasi Ruang Warna YCrCb (Metode Pengolahan Citra Digital Klasik):
        1. Konversi BGR ke YCrCb
        2. Thresholding rentang warna kulit manusia: Y in [0, 255], Cr in [133, 173], Cb in [77, 127]
        3. Operasi morfologi (Opening & Closing) untuk menghilangkan derau
        4. Ekstraksi kontur dengan rasio aspek wajah (0.7 s/d 1.6)
        """
        img_h, img_w = image.shape[:2]
        ycrcb = cv2.cvtColor(image, cv2.COLOR_BGR2YCrCb)
        
        # Ambang batas warna kulit standar Chai & Ngan
        lower_skin = np.array([0, 133, 77], dtype=np.uint8)
        upper_skin = np.array([255, 173, 127], dtype=np.uint8)
        mask = cv2.inRange(ycrcb, lower_skin, upper_skin)

        # Operasi morfologi: hilangkan noise kecil dan satukan lubang pada area wajah
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=2)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        faces = []

        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)
            if w >= min_size[0] and h >= min_size[1]:
                aspect_ratio = float(h) / float(w)
                # Rasio aspek wajah manusia proporsional antara 0.75 s/d 2.0
                if 0.75 <= aspect_ratio <= 2.0:
                    faces.append((x, y, w, h))

        return faces

    def detect_faces(
        self,
        image: np.ndarray,
        scale_factor: float = 1.15,
        min_neighbors: int = 5,
        min_size: Tuple[int, int] = (60, 60)
    ) -> List[Tuple[int, int, int, int]]:
        """Mendeteksi wajah menggunakan Haar Cascade jika tersedia, atau YCrCb segmentasi."""
        if self.has_cascade and self.face_cascade is not None:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
            faces = self.face_cascade.detectMultiScale(
                gray,
                scaleFactor=scale_factor,
                minNeighbors=min_neighbors,
                minSize=min_size,
                flags=cv2.CASCADE_SCALE_IMAGE
            )
            if len(faces) > 0:
                return [tuple(map(int, f)) for f in faces]

        # Fallback ke metode segmentasi warna kulit YCrCb
        return self.detect_faces_ycrcb(image, min_size)

    def align_face(self, face: np.ndarray) -> np.ndarray:
        """
        Penyejajaran Wajah Berbasis Deteksi Sepasang Mata (Eye Alignment):
        Mendeteksi mata kiri dan kanan, lalu menghitung sudut kemiringan (angle).
        Jika terdeteksi miring (hingga +-30 derajat), dilakukan transformasi rotasi afin
        sehingga garis antar mata sejajar horizontal sebelum ekstraksi ciri LBPH.
        """
        if self.eye_cascade is None or face is None or face.size == 0:
            return face
        
        h, w = face.shape[:2]
        gray = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY) if len(face.shape) == 3 else face
        upper_face = gray[:int(h * 0.6)]
        
        try:
            eyes = self.eye_cascade.detectMultiScale(
                upper_face,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(max(8, w // 10), max(8, w // 10))
            )
            if len(eyes) < 2:
                return face

            eyes = sorted(eyes, key=lambda e: e[2] * e[3], reverse=True)[:2]
            (x1, y1, w1, h1), (x2, y2, w2, h2) = sorted(eyes, key=lambda e: e[0])
            c1 = (x1 + w1 / 2.0, y1 + h1 / 2.0)
            c2 = (x2 + w2 / 2.0, y2 + h2 / 2.0)

            if abs(c2[0] - c1[0]) < w * 0.2:
                return face

            dy = c2[1] - c1[1]
            dx = c2[0] - c1[0]
            angle = float(np.degrees(np.arctan2(dy, dx)))

            if abs(angle) > 30:
                return face

            M = cv2.getRotationMatrix2D((w / 2.0, h / 2.0), angle, 1.0)
            aligned = cv2.warpAffine(face, M, (w, h), borderMode=cv2.BORDER_REPLICATE)
            return aligned
        except Exception:
            return face

    def detect_primary_face(
        self,
        image: np.ndarray,
        scale_factor: float = 1.15,
        min_neighbors: int = 5,
        min_size: Tuple[int, int] = (60, 60),
        align: bool = True
    ) -> Tuple[Optional[Tuple[int, int, int, int]], Optional[np.ndarray]]:
        """Mendeteksi wajah utama penumpang terdekat dari boarding gate dengan opsi eye alignment."""
        faces = self.detect_faces(image, scale_factor, min_neighbors, min_size)
        if not faces:
            return None, None

        # Prioritaskan wajah terluas
        primary_face = max(faces, key=lambda rect: rect[2] * rect[3])
        x, y, w, h = primary_face

        img_h, img_w = image.shape[:2]
        pad_x = int(w * 0.05)
        pad_y = int(h * 0.05)
        
        x_start = max(0, x - pad_x)
        y_start = max(0, y - pad_y)
        x_end = min(img_w, x + w + pad_x)
        y_end = min(img_h, y + h + pad_y)

        face_roi = image[y_start:y_end, x_start:x_end].copy()
        if align:
            face_roi = self.align_face(face_roi)

        return (x, y, w, h), face_roi

    def draw_gate_hud(
        self,
        image: np.ndarray,
        bbox: Optional[Tuple[int, int, int, int]],
        status_text: str = "SCANNING",
        is_success: Optional[bool] = None,
        passenger_name: Optional[str] = None
    ) -> np.ndarray:
        """Visual overlay modern Smart Gate KAI pada frame kamera."""
        canvas = image.copy()
        h, w = canvas.shape[:2]

        if is_success is True:
            color = (36, 179, 75)   # Green
            glow_text = "ACCESS GRANTED - GATE OPEN"
        elif is_success is False:
            color = (50, 50, 220)   # Red
            glow_text = "ACCESS DENIED - UNVERIFIED"
        else:
            color = (237, 107, 35)  # KAI Orange
            glow_text = status_text

        if bbox is None:
            cx, cy = w // 2, h // 2
            fw, fh = 200, 240
            gx1, gy1 = cx - fw // 2, cy - fh // 2
            gx2, gy2 = cx + fw // 2, cy + fh // 2
            cv2.rectangle(canvas, (gx1, gy1), (gx2, gy2), (180, 180, 180), 1, cv2.LINE_AA)
            cv2.putText(canvas, "Arahkan Wajah ke Bingkai", (gx1 - 10, gy1 - 12),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (220, 220, 220), 1, cv2.LINE_AA)
        else:
            x, y, bw, bh = bbox
            corner_len = int(min(bw, bh) * 0.2)
            thick = 3
            # Corners
            cv2.line(canvas, (x, y), (x + corner_len, y), color, thick)
            cv2.line(canvas, (x, y), (x, y + corner_len), color, thick)
            cv2.line(canvas, (x + bw, y), (x + bw - corner_len, y), color, thick)
            cv2.line(canvas, (x + bw, y), (x + bw, y + corner_len), color, thick)
            cv2.line(canvas, (x, y + bh), (x + corner_len, y + bh), color, thick)
            cv2.line(canvas, (x, y + bh), (x, y + bh - corner_len), color, thick)
            cv2.line(canvas, (x + bw, y + bh), (x + bw - corner_len, y + bh), color, thick)
            cv2.line(canvas, (x + bw, y + bh), (x + bw, y + bh - corner_len), color, thick)

            label = passenger_name if passenger_name else glow_text
            cv2.rectangle(canvas, (x, max(0, y - 28)), (x + bw, max(0, y)), color, -1)
            cv2.putText(canvas, label, (x + 6, max(0, y - 8)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 2, cv2.LINE_AA)

        return canvas
