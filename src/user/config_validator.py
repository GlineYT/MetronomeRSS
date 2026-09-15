"""
Stage 2: Configuration Validator
Validates the structure and fields of the configuration.
"""
import logging
from typing import Any

logger = logging.getLogger(__name__)

# Error codes
ERR_MISSING_METADATA = "ERR_MISSING_METADATA"
ERR_MISSING_PREFERENCES = "ERR_MISSING_PREFERENCES"
ERR_MISSING_GUID = "ERR_MISSING_GUID"
ERR_INVALID_GUID = "ERR_INVALID_GUID"
ERR_INVALID_COLOR = "ERR_INVALID_COLOR"
ERR_INVALID_LANGUAGE = "ERR_INVALID_LANGUAGE"
ERR_INVALID_BOOLEAN = "ERR_INVALID_BOOLEAN"
ERR_INVALID_INTEGER = "ERR_INVALID_INTEGER"
ERR_INVALID_STRING = "ERR_INVALID_STRING"
ERR_INVALID_ARRAY = "ERR_INVALID_ARRAY"
ERR_INVALID_CATEGORY = "ERR_INVALID_CATEGORY"
ERR_INVALID_FEED = "ERR_INVALID_FEED"
ERR_INVALID_ITEM = "ERR_INVALID_ITEM"

# Valid language codes (ISO 639-1)
VALID_LANGUAGES = {"en", "fr", "de", "es", "it", "pt", "ru", "zh", "ja", "ar"}

def validate_config(data: dict[str, Any]) -> tuple[bool, str | None]:
    """
    Stage 2: Validate the configuration structure and fields.

    Args:
        data: Configuration dictionary to validate

    Returns:
        Tuple of (is_valid, error_code)
    """
    logger.info("Validating configuration")

    # Check required top-level sections
    if "metadata" not in data:
        logger.error("Missing metadata section")
        return False, ERR_MISSING_METADATA

    if "preferences" not in data:
        logger.error("Missing preferences section")
        return False, ERR_MISSING_PREFERENCES

    # Validate metadata
    valid, error = validate_metadata(data["metadata"])
    if not valid:
        return False, error

    # Validate preferences
    valid, error = validate_preferences(data["preferences"])
    if not valid:
        return False, error

    # Validate feeds (if present)
    if "feeds" in data:
        valid, error = validate_feeds(data["feeds"])
        if not valid:
            return False, error

    logger.info("Configuration validation passed")
    return True, None


def validate_metadata(metadata: dict[str, Any]) -> tuple[bool, str | None]:
    """Validate the metadata section."""
    logger.info("Validating metadata")

    # GUID is required
    if "guid" not in metadata:
        logger.error("Missing GUID in metadata")
        return False, ERR_MISSING_GUID

    guid = metadata["guid"]
    if not isinstance(guid, str) or len(guid) < 32:
        logger.error(f"Invalid GUID format: {guid}")
        return False, ERR_INVALID_GUID

    # Check for required fields (optional but should exist)
    required_fields = ["created_date", "created_time", "modified_date", "modified_time"]
    for field in required_fields:
        if field in metadata and not isinstance(metadata[field], str):
            logger.warning(f"Field {field} should be a string, got {type(metadata[field]).__name__}")

    return True, None


def validate_preferences(preferences: dict[str, Any]) -> tuple[bool, str | None]:
    """Validate the preferences section."""
    logger.info("Validating preferences")

    # Validate color theme
    if "color_theme" in preferences:
        valid, error = validate_color(preferences["color_theme"])
        if not valid:
            return False, error

    # Validate language
    if "language" in preferences:
        lang = preferences["language"]
        if not isinstance(lang, str):
            logger.error(f"Language must be a string, got {type(lang).__name__}")
            return False, ERR_INVALID_LANGUAGE
        if lang not in VALID_LANGUAGES:
            logger.warning(f"Unknown language code: {lang} (using any string)")

    # Validate user_dir (must be a string)
    if "user_dir" in preferences and not isinstance(preferences["user_dir"], str):
            logger.error("user_dir must be a string")
            return False, ERR_INVALID_STRING

    # Validate caching_enabled (must be boolean)
    if "caching_enabled" in preferences and not isinstance(preferences["caching_enabled"], bool):
            logger.error("caching_enabled must be a boolean")
            return False, ERR_INVALID_BOOLEAN

    # Validate update_interval (must be an integer)
    if "update_interval" in preferences:
        if not isinstance(preferences["update_interval"], int):
            logger.error("update_interval must be an integer")
            return False, ERR_INVALID_INTEGER
        if preferences["update_interval"] < 0:
            logger.error(f"Invalid update_interval: {preferences['update_interval']}")
            return False, ERR_INVALID_INTEGER

    # Validate favourites (must be a list of strings)
    if "favourites" in preferences:
        favs = preferences["favourites"]
        if not isinstance(favs, list):
            logger.error("favourites must be a list")
            return False, ERR_INVALID_ARRAY
        for fav in favs:
            if not isinstance(fav, str):
                logger.error("favourites must contain strings")
                return False, ERR_INVALID_STRING

    # Validate read_items (must be a list of strings)
    if "read_items" in preferences:
        items = preferences["read_items"]
        if not isinstance(items, list):
            logger.error("read_items must be a list")
            return False, ERR_INVALID_ARRAY
        for item in items:
            if not isinstance(item, str):
                logger.error("read_items must contain strings")
                return False, ERR_INVALID_STRING

    # Validate bookmarked_items (must be a list of strings)
    if "bookmarked_items" in preferences:
        items = preferences["bookmarked_items"]
        if not isinstance(items, list):
            logger.error("bookmarked_items must be a list")
            return False, ERR_INVALID_ARRAY
        for item in items:
            if not isinstance(item, str):
                logger.error("bookmarked_items must contain strings")
                return False, ERR_INVALID_STRING

    # Validate blacklist (must be a list of strings)
    if "blacklist" in preferences:
        blacklist = preferences["blacklist"]
        if not isinstance(blacklist, list):
            logger.error("blacklist must be a list")
            return False, ERR_INVALID_ARRAY
        for domain in blacklist:
            if not isinstance(domain, str):
                logger.error("blacklist must contain strings")
                return False, ERR_INVALID_STRING

    # Validate categories
    if "categories" in preferences:
        valid, error = validate_categories(preferences["categories"])
        if not valid:
            return False, error

    return True, None


def validate_color(color: dict[str, Any]) -> tuple[bool, str | None]:
    """Validate a color object."""
    if not isinstance(color, dict):
        logger.error("Color must be an object")
        return False, ERR_INVALID_COLOR

    required = ["r", "g", "b"]
    for field in required:
        if field not in color:
            logger.error(f"Color missing {field} field")
            return False, ERR_INVALID_COLOR
        if not isinstance(color[field], int):
            logger.error(f"Color {field} must be an integer")
            return False, ERR_INVALID_COLOR
        if color[field] < 0 or color[field] > 255:
            logger.error(f"Color {field} must be between 0 and 255")
            return False, ERR_INVALID_COLOR

    return True, None


def validate_categories(categories: list) -> tuple[bool, str | None]:
    """Validate categories list."""
    if not isinstance(categories, list):
        logger.error("Categories must be a list")
        return False, ERR_INVALID_CATEGORY

    for idx, cat in enumerate(categories):
        if not isinstance(cat, dict):
            logger.error(f"Category {idx} must be an object")
            return False, ERR_INVALID_CATEGORY

        # Name is required
        if "name" not in cat or not isinstance(cat["name"], str):
            logger.error(f"Category {idx} missing name or name not a string")
            return False, ERR_INVALID_CATEGORY

        # Icon is optional but must be string if present
        if "icon" in cat and not isinstance(cat["icon"], str):
            logger.error(f"Category {idx} icon must be a string")
            return False, ERR_INVALID_CATEGORY

        # bind_patterns must be a list if present
        if "bind_patterns" in cat:
            if not isinstance(cat["bind_patterns"], list):
                logger.error(f"Category {idx} bind_patterns must be a list")
                return False, ERR_INVALID_CATEGORY
            for pattern in cat["bind_patterns"]:
                if not isinstance(pattern, str):
                    logger.error(f"Category {idx} bind_patterns must contain strings")
                    return False, ERR_INVALID_CATEGORY

        # is_default must be boolean if present
        if "is_default" in cat and not isinstance(cat["is_default"], bool):
            logger.error(f"Category {idx} is_default must be a boolean")
            return False, ERR_INVALID_CATEGORY

    return True, None


def validate_feeds(feeds: list) -> tuple[bool, str | None]:
    """Validate feeds list."""
    if not isinstance(feeds, list):
        logger.error("Feeds must be a list")
        return False, ERR_INVALID_FEED

    for idx, feed in enumerate(feeds):
        if not isinstance(feed, dict):
            logger.error(f"Feed {idx} must be an object")
            return False, ERR_INVALID_FEED

        # Link is required
        if "link" not in feed or not isinstance(feed["link"], str):
            logger.error(f"Feed {idx} missing link or link not a string")
            return False, ERR_INVALID_FEED

        # Category is optional but must be string if present
        if "category" in feed and not isinstance(feed["category"], str):
            logger.error(f"Feed {idx} category must be a string")
            return False, ERR_INVALID_FEED

        # Language is optional but must be string if present
        if "language" in feed and not isinstance(feed["language"], str):
            logger.error(f"Feed {idx} language must be a string")
            return False, ERR_INVALID_FEED

        # Validate items
        if "items" in feed:
            valid, error = validate_items(feed["items"])
            if not valid:
                return False, error

    return True, None


def validate_items(items: list) -> tuple[bool, str | None]:
    """Validate items list."""
    if not isinstance(items, list):
        logger.error("Items must be a list")
        return False, ERR_INVALID_ITEM

    for idx, item in enumerate(items):
        if not isinstance(item, dict):
            logger.error(f"Item {idx} must be an object")
            return False, ERR_INVALID_ITEM

        # GUID is required
        if "guid" not in item or not isinstance(item["guid"], str):
            logger.error(f"Item {idx} missing guid or guid not a string")
            return False, ERR_INVALID_ITEM

        # Title is recommended but not required
        if "title" in item and not isinstance(item["title"], str):
            logger.error(f"Item {idx} title must be a string")
            return False, ERR_INVALID_ITEM

    return True, None
