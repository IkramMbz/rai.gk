from pathlib import Path

EXCLUDED_EXTENSIONS = {
    ".eot", ".ttf", ".woff", ".woff2", ".otf",
    ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".svg", ".webp", ".avif", ".ico", ".tiff",
    ".mp4", ".avi", ".mov", ".mkv", ".webm", ".flv", ".wmv", ".m4v",
    ".frm", ".ibd", ".map"
}

EXCLUDED_SUFFIXES = ("_fsm", "_vm")

def is_excluded(filename):
    return (
        Path(filename).suffix.lower() in EXCLUDED_EXTENSIONS
        or filename.endswith(EXCLUDED_SUFFIXES)
        or filename.isdigit()
    )
