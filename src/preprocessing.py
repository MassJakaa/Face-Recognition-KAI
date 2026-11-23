import cv2
import numpy as np
from typing import Tuple, Dict
from src.config import (
    FACE_TARGET_SIZE,
    CLAHE_CLIP_LIMIT,
    CLAHE_GRID_SIZE,
    BILATERAL_D,
    BILATERAL_SIGMA_COLOR,
    BILATERAL_SIGMA_SPACE
)

class ImagePreprocessor:
    """
    Modul Prapemrosesan Citra Wajah untuk Sistem Face Recognition KAI.
    Menerapkan pipeline standar pengolahan citra digital:
    1. Konversi ruang warna (BGR ke Grayscale)
    2. Reduksi derau adaptif menggunakan Bilateral Filter
    3. Normalisasi pencahayaan menggunakan CLAHE (Contrast Limited Adaptive Histogram Equalization)
    4. Normalisasi resolusi dan geometri (Resize bicubic ke ukuran standar)
    """

    def __init__(self, target_size: Tuple[int, int] = FACE_TARGET_SIZE):
        self.target_size = target_size
        self.clahe = cv2.createCLAHE(
            clipLimit=CLAHE_CLIP_LIMIT,
            tileGridSize=CLAHE_GRID_SIZE
        )

    def to_grayscale(self, image: np.ndarray) -> np.ndarray:
        """Mengonversi citra BGR ke Grayscale (bobot standar ITU-R BT.601)."""
        if len(image.shape) == 2:
            return image
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    def denoise_bilateral(self, gray_image: np.ndarray) -> np.ndarray:
        """
        Reduksi derau citra wajah dengan Bilateral Filter.
        Keunggulan: Menghaluskan tekstur kulit tanpa mengaburkan tepi penting (mata, hidung, bibir).
        """
        return cv2.bilateralFilter(
            gray_image,
            d=BILATERAL_D,
            sigmaColor=BILATERAL_SIGMA_COLOR,
            sigmaSpace=BILATERAL_SIGMA_SPACE
        )

    def apply_clahe(self, gray_image: np.ndarray) -> np.ndarray:
        """
        Peningkatan kontras adaptif lokal dengan CLAHE.
        Mengatasi masalah pencahayaan ekstrem (backlight, bayangan, atau lampu stasiun yang silau).
        """
        return self.clahe.apply(gray_image)

    def apply_standard_hist_eq(self, gray_image: np.ndarray) -> np.ndarray:
        """Ekualisasi histogram global konvensional (untuk perbandingan visual di evaluasi)."""
        return cv2.equalizeHist(gray_image)

    def normalize_geometry(self, image: np.ndarray) -> np.ndarray:
        """Standardisasi ukuran citra wajah ke target_size menggunakan interpolasi bicubic."""
        return cv2.resize(image, self.target_size, interpolation=cv2.INTER_CUBIC)

    def process(self, face_roi: np.ndarray) -> np.ndarray:
        """
        Pipeline lengkap prapemrosesan citra wajah:
        Input: BGR Face Crop
        Output: Normalized CLAHE Grayscale Face
        """
        gray = self.to_grayscale(face_roi)
        denoised = self.denoise_bilateral(gray)
        enhanced = self.apply_clahe(denoised)
        normalized = self.normalize_geometry(enhanced)
        return normalized

    def get_intermediate_stages(self, face_roi: np.ndarray) -> Dict[str, np.ndarray]:
        """
        Menghasilkan seluruh citra tahapan perantara untuk keperluan analisis,
        visualisasi GUI Streamlit, dan dokumentasi laporan ilmiah.
        """
        gray = self.to_grayscale(face_roi)
        denoised = self.denoise_bilateral(gray)
        hist_eq = self.apply_standard_hist_eq(gray)
        clahe_enhanced = self.apply_clahe(denoised)
        normalized = self.normalize_geometry(clahe_enhanced)

        return {
            "1. Citra Asli (ROI BGR)": face_roi,
            "2. Grayscale (Luminansi)": gray,
            "3. Reduksi Derau (Bilateral)": denoised,
            "4. Ekualisasi Global (Standar)": hist_eq,
            "5. Peningkatan Kontras Adaptif (CLAHE)": clahe_enhanced,
            "6. Normalisasi Ukuran (128x128)": normalized
        }
