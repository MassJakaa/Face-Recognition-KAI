import numpy as np
import cv2
from typing import Tuple, List, Dict, Optional
from src.config import LBP_RADIUS, LBP_NEIGHBORS, LBP_GRID_X, LBP_GRID_Y

class LBPHFeatureExtractor:
    """
    Ekstraktor Fitur Tekstur Wajah menggunakan Local Binary Patterns Histograms (LBPH).
    Diimplementasikan murni berbasis NumPy dan Scipy untuk transparansi matematis:
    1. Komputasi matriks LBP 8-tetangga circular/grid.
    2. Segmentasi spasial menjadi grid sel (LBP_GRID_X x LBP_GRID_Y).
    3. Ekstraksi histogram lokal per sel dan normalisasi L1.
    4. Penggabungan (concatenation) menjadi vektor fitur global spasial.
    5. Pengukuran jarak menggunakan Chi-Square Distance (metrik standar histogram).
    """

    def __init__(self, grid_x: int = LBP_GRID_X, grid_y: int = LBP_GRID_Y):
        self.grid_x = grid_x
        self.grid_y = grid_y

    def compute_lbp_image(self, gray_img: np.ndarray) -> np.ndarray:
        """
        Menghitung representasi citra LBP 2D (uint8) dari citra grayscale.
        Formula:
            LBP(xc, yc) = sum_{p=0..7} s(i_p - i_c) * 2^p
            di mana s(x) = 1 jika x >= 0, dan 0 sebaliknya.
        """
        h, w = gray_img.shape
        # Menggunakan slicing tervektorisasi untuk kecepatan komputasi tinggi
        center = gray_img[1:h-1, 1:w-1].astype(np.int32)
        
        # 8 Tetangga berlawanan arah jarum jam (p0 s/d p7)
        # p0: (0, 1), p1: (-1, 1), p2: (-1, 0), p3: (-1, -1),
        # p4: (0, -1), p5: (1, -1), p6: (1, 0), p7: (1, 1)
        p0 = gray_img[1:h-1, 2:w  ] >= center
        p1 = gray_img[0:h-2, 2:w  ] >= center
        p2 = gray_img[0:h-2, 1:w-1] >= center
        p3 = gray_img[0:h-2, 0:w-2] >= center
        p4 = gray_img[1:h-1, 0:w-2] >= center
        p5 = gray_img[2:h  , 0:w-2] >= center
        p6 = gray_img[2:h  , 1:w-1] >= center
        p7 = gray_img[2:h  , 2:w  ] >= center

        lbp = (p0.astype(np.uint8) * 1 +
               p1.astype(np.uint8) * 2 +
               p2.astype(np.uint8) * 4 +
               p3.astype(np.uint8) * 8 +
               p4.astype(np.uint8) * 16 +
               p5.astype(np.uint8) * 32 +
               p6.astype(np.uint8) * 64 +
               p7.astype(np.uint8) * 128)

        # Padding 1 piksel di batas tepi agar dimensi tetap sama dengan citra asli
        lbp_padded = np.pad(lbp, pad_width=1, mode='edge')
        return lbp_padded.astype(np.uint8)

    def extract_features(self, preprocessed_face: np.ndarray) -> np.ndarray:
        """
        Mengekstrak vektor fitur histogram spasial LBPH.
        Output: Vektor 1D float32 berukuran (grid_x * grid_y * 256)
        """
        lbp_img = self.compute_lbp_image(preprocessed_face)
        h, w = lbp_img.shape
        cell_h = h // self.grid_y
        cell_w = w // self.grid_x

        histograms = []
        for r in range(self.grid_y):
            for c in range(self.grid_x):
                r_start, r_end = r * cell_h, (r + 1) * cell_h
                c_start, c_end = c * cell_w, (c + 1) * cell_w
                cell = lbp_img[r_start:r_end, c_start:c_end]
                
                # Hitung histogram 256 bin untuk sel ini
                hist, _ = np.histogram(cell, bins=256, range=(0, 256))
                hist = hist.astype(np.float32)
                # Normalisasi L1
                norm = np.sum(hist)
                if norm > 0:
                    hist /= norm
                histograms.append(hist)

        # Gabungkan semua histogram sel menjadi satu vektor global
        feature_vector = np.concatenate(histograms)
        # Normalisasi global agar total bobot penjumlahan bernilai 1.0 (skala jarak 0 s/d 1)
        total_sum = np.sum(feature_vector)
        if total_sum > 0:
            feature_vector /= total_sum

        return feature_vector

    @staticmethod
    def chi_square_distance(hist1: np.ndarray, hist2: np.ndarray) -> float:
        """
        Menghitung Chi-Square Distance antara dua vektor histogram:
            D_chi = 0.5 * sum((h1_i - h2_i)^2 / (h1_i + h2_i + eps))
        Rentang: [0, 1] (0 = identik/sempurna, 1 = sangat berbeda)
        """
        eps = 1e-10
        denom = hist1 + hist2 + eps
        diff = hist1 - hist2
        distance = 0.5 * np.sum((diff ** 2) / denom)
        return float(distance)


class EigenfaceFeatureExtractor:
    """
    Ekstraktor Fitur Wajah menggunakan Principal Component Analysis (PCA / Eigenfaces).
    Metode fundamental pengolahan citra digital untuk reduksi dimensi dan proyeksi eigenspace.
    """

    def __init__(self, n_components: int = 16):
        self.n_components = n_components
        self.mean_face: Optional[np.ndarray] = None
        self.eigenfaces: Optional[np.ndarray] = None
        self.is_fitted: bool = False

    def fit(self, face_images: List[np.ndarray]):
        """
        Melatih PCA pada sekumpulan citra wajah:
        1. Vektorisasi citra 2D menjadi vektor 1D
        2. Hitung citra rata-rata (mean face)
        3. Dekomposisi SVD / Eigenvector pada matriks kovarian
        """
        if len(face_images) < 2:
            return

        # Flatten setiap wajah
        flat_faces = np.array([f.flatten().astype(np.float32) for f in face_images])
        self.mean_face = np.mean(flat_faces, axis=0)
        centered_faces = flat_faces - self.mean_face

        # SVD untuk efisiensi komputasi
        u, s, vt = np.linalg.svd(centered_faces, full_matrices=False)
        k = min(self.n_components, len(vt))
        self.eigenfaces = vt[:k]  # Shape: (k, 16384)
        self.is_fitted = True

    def extract_features(self, preprocessed_face: np.ndarray) -> np.ndarray:
        """Proyeksikan citra wajah ke ruang bobot eigen (eigenspace weight vector)."""
        if not self.is_fitted or self.mean_face is None or self.eigenfaces is None:
            # Fallback jika belum di-fit (misal dataset awal)
            return preprocessed_face.flatten().astype(np.float32)[:self.n_components]

        flat = preprocessed_face.flatten().astype(np.float32)
        diff = flat - self.mean_face
        # Bobot proyeksi: w_k = eigenfaces dot diff
        weights = np.dot(self.eigenfaces, diff)
        return weights

    @staticmethod
    def euclidean_distance(w1: np.ndarray, w2: np.ndarray) -> float:
        """Menghitung jarak Euclidean antar vektor bobot eigen."""
        return float(np.linalg.norm(w1 - w2))
