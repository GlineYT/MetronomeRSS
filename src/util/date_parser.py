"""
Utility for normalizing feed date strings into (date_str, time_str) tuples.

Handles:
    - RFC822 (RSS 2.0):    "Tue, 26 Oct 2004 14:01:01 -0500"
    - ISO 8601 with Z:     "2026-10-06T15:30:00Z"
    - ISO 8601 with offset:"2026-10-06T15:30:00+03:00"
    - ISO 8601 date only:  "2026-10-06"
    - Anything else:       returns ("", "") instead of crashing
"""
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


# --- Output format constants ---
DATE_FORMAT = "%d %b %Y"   # "06 Oct 2026"
TIME_FORMAT = "%H:%M"      # "15:30"


def parse_feed_date(raw: str) -> tuple[str, str]:
    """
    Parse a feed date string and return (date_str, time_str).

    Args:
        raw: The raw date string from the feed (RFC822, ISO 8601, or garbage).

    Returns:
        (date_str, time_str) formatted for display. Both are "" if parsing fails.
    """
    if not raw:
        return "", ""

    raw = raw.strip()
    dt = None

    # --- Try RFC822 first (RSS 2.0) ---
    # email.utils.parsedate_to_datetime is the canonical parser for this format
    try:
        from email.utils import parsedate_to_datetime
        dt = parsedate_to_datetime(raw)
    except (TypeError, ValueError):
        dt = None

    # --- Try ISO 8601 (Atom, DW, modern feeds) ---
    if dt is None:
        # Python 3.11+ doesn't understand the trailing 'Z' in fromisoformat,
        # so we replace it with '+00:00' which it does understand.
        iso_candidate = raw
        if iso_candidate.endswith("Z"):
            iso_candidate = iso_candidate[:-1] + "+00:00"

        try:
            dt = datetime.fromisoformat(iso_candidate)
        except ValueError:
            dt = None

    # --- Last resort: try a few common format strings ---
    if dt is None:
        fallback_formats = [
            "%a, %d %b %Y %H:%M:%S %z",      # RFC822 without a colon in offset
            "%Y-%m-%d %H:%M:%S",              # SQL-ish
            "%d/%m/%Y %H:%M",                 # European
            "%m/%d/%Y %H:%M",                 # US
        ]
        for fmt in fallback_formats:
            try:
                dt = datetime.strptime(raw, fmt)
                break
            except ValueError:
                continue

    # --- Still nothing? Give up gracefully. ---
    if dt is None:
        logger.warning(f"Could not parse date string: {raw!r}")
        return "", ""

    # --- Normalize timezone: convert to UTC for consistency ---
    # This means "15:30:00Z" and "18:30:00+03:00" both become "15:30".
    # If you'd rather keep local time, skip this block.
    if dt.tzinfo is not None:
        dt = dt.astimezone(timezone.utc)

    return dt.strftime(DATE_FORMAT), dt.strftime(TIME_FORMAT)
