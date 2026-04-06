from __future__ import annotations


def validate_csv(uploaded_file) -> bool:
    """Check if file is valid text CSV (basic header sanity)."""

    if not hasattr(uploaded_file, "stream"):
        return False
    try:
        uploaded_file.stream.seek(0)
        header = uploaded_file.stream.read(2)
        uploaded_file.stream.seek(0)
        return all(
            isinstance(b, int) and (32 <= b <= 126 or b in (9, 10, 13)) for b in header
        )
    except Exception:
        # If stream doesn't support this reliably, don't block upload.
        return True


def validate_pdf(uploaded_file) -> bool:
    """Check if file is valid PDF by header."""

    if not hasattr(uploaded_file, "stream"):
        return False
    try:
        uploaded_file.stream.seek(0)
        header = uploaded_file.stream.read(4)
        uploaded_file.stream.seek(0)
        return header.startswith(b"%PDF")
    except Exception:
        return False
