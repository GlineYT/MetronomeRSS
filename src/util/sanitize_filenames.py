import re

def sanitize_profile_name(name: str, max_length: int = 64) -> str:
    """Sanitize a profile name for safe use as a filename."""
    # Replace unsafe characters with underscore
    sanitized = re.sub(r'[^\w\s\-]', '_', name)

    # Collapse whitespace/underscores
    sanitized = re.sub(r'[\s_]+', '_', sanitized)

    # Strip leading/trailing
    sanitized = sanitized.strip('_ ')

    # Remove leading dots (hidden files)
    sanitized = sanitized.lstrip('.')

    # Truncate
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length].rstrip('_ ')

    # Handle reserved names (Windows)
    reserved = {"CON", "PRN", "AUX", "NUL",
                "COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8", "COM9",
                "LPT1", "LPT2", "LPT3", "LPT4", "LPT5", "LPT6", "LPT7", "LPT8", "LPT9"}
    if sanitized.upper() in reserved:
        sanitized = f"_{sanitized}"

    # Fallback
    if not sanitized:
        sanitized = "profile"

    return sanitized

