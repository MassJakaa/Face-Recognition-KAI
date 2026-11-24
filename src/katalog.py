"""Katalog kereta -> rute. Dropdown relasi mengikuti kereta yang dipilih.
Contoh data; sesuaikan sendiri. Format nama kereta/stasiun sama dengan yang sudah dipakai di app."""

RUTE_KERETA = {
    "Argo Parahyangan (KA 35)":  ("Gambir (GMR)", "Bandung (BD)"),
    "Taksaka (KA 68)":           ("Gambir (GMR)", "Yogyakarta (YK)"),
    "Argo Bromo Anggrek (KA 2)": ("Gambir (GMR)", "Surabaya Pasarturi (SBI)"),
    "Lodaya (KA 92)":            ("Bandung (BD)", "Solo Balapan (SLO)"),
    "Gajayana (KA 55)":          ("Gambir (GMR)", "Malang (ML)"),
    "Turangga (KA 65)":          ("Surabaya Gubeng (SGU)", "Bandung (BD)"),
    "Sembrani (KA 63)":          ("Gambir (GMR)", "Surabaya Pasarturi (SBI)"),
}


def relasi_opsi(nama_kereta: str):
    """Dua arah rute untuk kereta tersebut, mis. ['A - B', 'B - A']."""
    a, b = RUTE_KERETA[nama_kereta]
    return [f"{a} - {b}", f"{b} - {a}"]
