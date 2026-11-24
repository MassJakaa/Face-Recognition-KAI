def validate_nik(nik: str):
    """NIK harus 16 digit angka. Return (ok, pesan)."""
    nik = (nik or "").strip()
    if not (nik.isascii() and nik.isdigit()):
        return False, "NIK hanya boleh berisi angka."
    if len(nik) != 16:
        return False, f"NIK harus 16 digit (sekarang {len(nik)} digit)."
    return True, ""
