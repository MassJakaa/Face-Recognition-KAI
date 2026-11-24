import sqlite3
import numpy as np
import os
import pickle
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple, Any
from src.config import DB_PATH

class DatabaseManager:
    """
    Pengelola Basis Data SQLite untuk Sistem KAI Face Recognition Boarding Gate.
    Menyimpan data penumpang, tiket kereta api aktif, fitur biometrik wajah,
    dan catatan audit log transaksi boarding.
    """

    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        """Membuat tabel jika belum ada."""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Tabel Penumpang
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS passengers (
                    nik TEXT PRIMARY KEY,
                    nama TEXT NOT NULL,
                    jenis_kelamin TEXT NOT NULL,
                    telepon TEXT,
                    foto_path TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Tabel Tiket Kereta (Manifest Perjalanan)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tickets (
                    ticket_code TEXT PRIMARY KEY,
                    nik TEXT NOT NULL,
                    nama_kereta TEXT NOT NULL,
                    relasi TEXT NOT NULL,
                    jadwal_berangkat TIMESTAMP NOT NULL,
                    gerbong_kursi TEXT NOT NULL,
                    status_tiket TEXT DEFAULT 'ACTIVE',
                    waktu_boarding TIMESTAMP,
                    FOREIGN KEY(nik) REFERENCES passengers(nik)
                )
            """)

            # Tabel Vektor Fitur Wajah (Biometrik Template)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS face_templates (
                    template_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nik TEXT NOT NULL,
                    method TEXT NOT NULL,
                    feature_vector BLOB NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(nik) REFERENCES passengers(nik)
                )
            """)

            # Tabel Audit Log Boarding Gate
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS gate_logs (
                    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    gate_id TEXT NOT NULL,
                    nik_matched TEXT,
                    nama_penumpang TEXT,
                    ticket_code TEXT,
                    confidence REAL,
                    distance REAL,
                    status TEXT NOT NULL,
                    pesan TEXT NOT NULL
                )
            """)
            conn.commit()

    def save_passenger(self, nik: str, nama: str, jenis_kelamin: str, telepon: str, foto_path: str = ""):
        with self._get_connection() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO passengers (nik, nama, jenis_kelamin, telepon, foto_path)
                VALUES (?, ?, ?, ?, ?)
            """, (nik, nama, jenis_kelamin, telepon, foto_path))
            conn.commit()

    def save_face_template(self, nik: str, method: str, feature_vector: np.ndarray):
        vector_bytes = pickle.dumps(feature_vector)
        with self._get_connection() as conn:
            # Hapus template lama jika ada method yang sama
            conn.execute("DELETE FROM face_templates WHERE nik = ? AND method = ?", (nik, method))
            conn.execute("""
                INSERT INTO face_templates (nik, method, feature_vector)
                VALUES (?, ?, ?)
            """, (nik, method, vector_bytes))
            conn.commit()

    def save_ticket(self, ticket_code: str, nik: str, nama_kereta: str, relasi: str,
                    jadwal_berangkat: str, gerbong_kursi: str, status_tiket: str = "ACTIVE"):
        with self._get_connection() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO tickets 
                (ticket_code, nik, nama_kereta, relasi, jadwal_berangkat, gerbong_kursi, status_tiket)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (ticket_code, nik, nama_kereta, relasi, jadwal_berangkat, gerbong_kursi, status_tiket))
            conn.commit()

    def next_ticket_code(self) -> str:
        """Kode tiket berikutnya yang belum dipakai: KAI-000001, KAI-000002, ..."""
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT MAX(CAST(SUBSTR(ticket_code, 5) AS INTEGER)) FROM tickets "
                "WHERE ticket_code GLOB 'KAI-[0-9][0-9][0-9][0-9][0-9][0-9]'"
            ).fetchone()
        return f"KAI-{(row[0] or 0) + 1:06d}"

    def get_all_templates(self, method: str = "LBPH") -> List[Dict[str, Any]]:
        """Mengambil seluruh biometrik wajah terdaftar untuk pencocokan 1:N."""
        with self._get_connection() as conn:
            rows = conn.execute("""
                SELECT ft.nik, p.nama, p.foto_path, ft.feature_vector
                FROM face_templates ft
                JOIN passengers p ON ft.nik = p.nik
                WHERE ft.method = ?
            """, (method,)).fetchall()
            
            templates = []
            for r in rows:
                templates.append({
                    "nik": r["nik"],
                    "nama": r["nama"],
                    "foto_path": r["foto_path"],
                    "feature_vector": pickle.loads(r["feature_vector"])
                })
            return templates

    def get_passenger(self, nik: str) -> Optional[Dict[str, Any]]:
        with self._get_connection() as conn:
            row = conn.execute("SELECT * FROM passengers WHERE nik = ?", (nik,)).fetchone()
            return dict(row) if row else None

    def get_active_ticket_for_passenger(self, nik: str) -> Optional[Dict[str, Any]]:
        """Mencari tiket aktif untuk NIK yang cocok."""
        with self._get_connection() as conn:
            row = conn.execute("""
                SELECT * FROM tickets 
                WHERE nik = ?
                ORDER BY jadwal_berangkat ASC
                LIMIT 1
            """, (nik,)).fetchone()
            return dict(row) if row else None

    def mark_ticket_boarded(self, ticket_code: str):
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self._get_connection() as conn:
            conn.execute("""
                UPDATE tickets 
                SET status_tiket = 'BOARDED', waktu_boarding = ?
                WHERE ticket_code = ?
            """, (now_str, ticket_code))
            conn.commit()

    def log_gate_event(self, gate_id: str, status: str, pesan: str,
                       nik: Optional[str] = None, nama: Optional[str] = None,
                       ticket_code: Optional[str] = None,
                       confidence: float = 0.0, distance: float = 0.0):
        with self._get_connection() as conn:
            conn.execute("""
                INSERT INTO gate_logs (gate_id, nik_matched, nama_penumpang, ticket_code, confidence, distance, status, pesan)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (gate_id, nik, nama, ticket_code, confidence, distance, status, pesan))
            conn.commit()

    def get_recent_logs(self, limit: int = 50) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM gate_logs ORDER BY timestamp DESC LIMIT ?
            """, (limit,)).fetchall()
            return [dict(r) for r in rows]

    def get_all_passengers(self) -> List[Dict[str, Any]]:
        """Mengambil seluruh data akun penumpang terdaftar beserta status rekaman wajahnya."""
        with self._get_connection() as conn:
            rows = conn.execute("""
                SELECT p.nik, p.nama, p.jenis_kelamin, p.telepon, p.foto_path, p.created_at,
                       CASE WHEN ft.nik IS NOT NULL THEN 1 ELSE 0 END as has_face
                FROM passengers p
                LEFT JOIN face_templates ft ON p.nik = ft.nik
                GROUP BY p.nik
                ORDER BY p.created_at DESC
            """).fetchall()
            return [dict(r) for r in rows]

    def has_face_template(self, nik: str) -> bool:
        """Memeriksa apakah penumpang dengan NIK ini sudah merekam wajah biometrik."""
        with self._get_connection() as conn:
            row = conn.execute("SELECT 1 FROM face_templates WHERE nik = ?", (nik,)).fetchone()
            return row is not None

    def get_tickets_by_passenger(self, nik: str) -> List[Dict[str, Any]]:
        """Mengambil seluruh tiket yang dipesan oleh NIK tertentu."""
        with self._get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM tickets WHERE nik = ? ORDER BY jadwal_berangkat DESC
            """, (nik,)).fetchall()
            return [dict(r) for r in rows]

    def get_all_passengers_with_tickets(self) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            rows = conn.execute("""
                SELECT p.nik, p.nama, p.jenis_kelamin, p.telepon, 
                       t.ticket_code, t.nama_kereta, t.relasi, t.jadwal_berangkat, 
                       t.gerbong_kursi, t.status_tiket, t.waktu_boarding
                FROM passengers p
                LEFT JOIN tickets t ON p.nik = t.nik
                ORDER BY p.nama ASC
            """).fetchall()
            return [dict(r) for r in rows]
