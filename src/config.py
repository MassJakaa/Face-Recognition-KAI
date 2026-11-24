import os
import cv2

# Base directories
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
SAMPLE_FACES_DIR = os.path.join(DATA_DIR, "sample_faces")
EVAL_RESULTS_DIR = os.path.join(DATA_DIR, "evaluation_results")
DB_PATH = os.path.join(DATA_DIR, "kai_boarding.db")

# Image Processing Configuration
FACE_TARGET_SIZE = (128, 128)  # Standardized face dimension (width, height)
CLAHE_CLIP_LIMIT = 2.5
CLAHE_GRID_SIZE = (8, 8)
BILATERAL_D = 5
BILATERAL_SIGMA_COLOR = 35
BILATERAL_SIGMA_SPACE = 35

# LBPH (Local Binary Pattern Histogram) Parameters
LBP_RADIUS = 1
LBP_NEIGHBORS = 8
LBP_GRID_X = 8
LBP_GRID_Y = 8
LBP_SIMILARITY_THRESHOLD = 0.22  # Normalized Chi-Square distance threshold (< threshold is match)

# Haar Cascade Paths
HAAR_CASCADE_PATH = os.path.join(cv2.data.haarcascades, "haarcascade_frontalface_default.xml")
HAAR_EYE_PATH = os.path.join(cv2.data.haarcascades, "haarcascade_eye.xml")

# KAI Business Rules
TRAIN_DEPARTURE_GATE_WINDOW_HOURS = 2  # Boarding dibuka 2 jam sebelum keberangkatan
