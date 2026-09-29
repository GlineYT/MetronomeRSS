import re
import sys
import unicodedata


# --- Platform-specific limits ---
if sys.platform == "win32":
    MAX_NAME_LENGTH = 64  # Conservative; Windows total path limit is 260
    RESERVED_NAMES = {
        "CON", "PRN", "AUX", "NUL",
        "COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8", "COM9",
        "LPT1", "LPT2", "LPT3", "LPT4", "LPT5", "LPT6", "LPT7", "LPT8", "LPT9",
    }
    ILLEGAL_CHARS = re.compile(r'[<>:"/\\|?*\x00-\x1f]')
else:
    # Linux, macOS, BSD
    MAX_NAME_LENGTH = 255
    RESERVED_NAMES = set()  # No reserved names on Unix
    ILLEGAL_CHARS = re.compile(r'[/\x00]')  # Only / and null are illegal


def sanitize_profile_name(name: str) -> str:
    """Sanitize a profile name for safe use as a filename."""
    if not isinstance(name, str):
        raise ValueError("Name must be a string")

    # Normalize Unicode (avoid filesystem encoding surprises)
    name = unicodedata.normalize("NFKC", name)

    # Replace illegal characters (platform-specific)
    sanitized = ILLEGAL_CHARS.sub("_", name)

    # Collapse whitespace/underscores
    sanitized = re.sub(r"[\s_]+", "_", sanitized)

    # Strip leading/trailing whitespace, underscores, and dots
    sanitized = sanitized.strip("_ .")

    # Handle reserved names (only Windows has them)
    if RESERVED_NAMES and sanitized.upper() in RESERVED_NAMES:
        sanitized = f"_{sanitized}"

    # Truncate (platform-specific limit)
    if len(sanitized) > MAX_NAME_LENGTH:
        sanitized = sanitized[:MAX_NAME_LENGTH].rstrip("_ .")

    # Fallback
    if not sanitized:
        sanitized = "profile"

    return sanitized
