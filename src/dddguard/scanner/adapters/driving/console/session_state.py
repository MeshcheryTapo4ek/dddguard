from .scan_options import ScanOptions

_LAST_SCAN_OPTIONS: ScanOptions | None = None


def set_last_scan_options(options: ScanOptions) -> None:
    """
    Updates the in-memory session state with the latest scan options.
    """
    global _LAST_SCAN_OPTIONS
    _LAST_SCAN_OPTIONS = options


def get_last_scan_options() -> ScanOptions | None:
    """
    Retrieves the last scan options from memory.
    Returns None if no scan has been performed in this session.
    """
    return _LAST_SCAN_OPTIONS
