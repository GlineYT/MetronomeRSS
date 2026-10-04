import json
import logging
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)


def _append_unique(field, data, value):
    """
    Append value to data[field], deduplicating by 'link' for feeds.
    Returns True if appended, False if duplicate.
    """
    if field == "feeds" and isinstance(value, dict):
        existing = [f.get("link") for f in data[field]]
        if value.get("link") in existing:
            logger.warning(f"Feed already exists in '{field}': {value.get('link')}")
            return False
        data[field].append(value)
        logger.info(f"Appended feed to '{field}': {value.get('link')}")
        return True

    if value not in data[field]:
        data[field].append(value)
        logger.info(f"Appended to '{field}': {value}")
        return True
    logger.warning(f"'{value}' already exists in '{field}' — skipping")
    return False


def update_user_data(profile_path, field, action, value=None):
    """Generic CRUD for list fields in a profile."""
    profile_path = Path(profile_path)
    if not profile_path.exists():
        logger.error(f"Profile not found: {profile_path}")
        return None

    # --- Load ---
    try:
        with open(profile_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        logger.error(f"Failed to load profile {profile_path}: {e}")
        return None

    # --- Validate field ---
    if field not in data:
        logger.error(f"Field '{field}' does not exist in {profile_path}")
        return None
    if not isinstance(data[field], list):
        logger.error(f"Field '{field}' is not a list")
        return None

    # --- Perform action ---
    if action == "read":
        return data[field]

    elif action == "create":
        _append_unique(field, data, value)

    elif action == "delete":
        if value in data[field]:
            data[field].remove(value)
            logger.info(f"Removed from '{field}': {value}")
        else:
            logger.warning(f"'{value}' not found in '{field}'")
            return data[field]

    elif action == "update":
        if not isinstance(value, (tuple, list)) or len(value) != 2:
            logger.error("Action 'update' requires value to be a tuple (old, new)")
            return None
        old_value, new_value = value
        if old_value in data[field]:
            idx = data[field].index(old_value)
            data[field][idx] = new_value
            logger.info(f"Updated '{field}': {old_value} -> {new_value}")
        else:
            logger.warning(f"'{old_value}' not found in '{field}'")
            return data[field]

    else:
        logger.error(f"Unknown action '{action}'")
        return None

    # --- Metadata ---
    now = datetime.now()
    if "metadata" in data:
        data["metadata"]["modified_date"] = now.strftime("%Y-%m-%d")
        data["metadata"]["modified_time"] = now.strftime("%H:%M:%S")

    # --- Save ---
    try:
        with open(profile_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
    except OSError as e:
        logger.error(f"Failed to save profile: {e}")
        return None

    return data[field]


def add_feed_to_profile(profile_path, url, category="", language=""):
    """Add a feed object to the profile's feed list."""
    new_feed = {
        "link": url,
        "category": category,
        "language": language,
        "items": [],
    }
    return update_user_data(profile_path, "feeds", "create", new_feed)
