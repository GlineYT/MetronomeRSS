"""
Stage 3: Configuration Parser
Parses the configuration into typed dictionaries.
"""
import logging
from typing import Any

from src.user.config_structs import (
    Category,
    Color,
    Feed,
    Item,
    Metadata,
    Preferences,
    Profile,
)

logger = logging.getLogger(__name__)

def parse_config(data: dict[str, Any]) -> Profile | None:
    """
    Stage 3: Parse the configuration into a typed dictionary.

    Args:
        data: Validated configuration dictionary

    Returns:
        Profile object (TypedDict) or None on error
    """
    logger.info("Parsing configuration")


    # Parse metadata
    metadata = parse_metadata(data.get("metadata", {}))

    # Parse preferences
    preferences = parse_preferences(data.get("preferences", {}))

    # Parse feeds
    feeds = parse_feeds(data.get("feeds", []))

    profile: Profile = {
        "metadata": metadata,
        "preferences": preferences,
        "feeds": feeds,
    }

    logger.info("Configuration parsed successfully")
    return profile




def parse_metadata(data: dict[str, Any]) -> Metadata:
    """Parse metadata into a typed dict."""
    return {
        "guid": data.get("guid", ""),
        "created_date": data.get("created_date", ""),
        "created_time": data.get("created_time", ""),
        "modified_date": data.get("modified_date", ""),
        "modified_time": data.get("modified_time", ""),
    }


def parse_preferences(data: dict[str, Any]) -> Preferences:
    """Parse preferences into a typed dict."""
    # Parse color
    color_data = data.get("color_theme", {})
    color: Color = {
        "r": color_data.get("r", 30),
        "g": color_data.get("g", 144),
        "b": color_data.get("b", 255),
    }

    # Parse categories
    categories = parse_categories(data.get("categories", []))

    return {
        "color_theme": color,
        "language": data.get("language", "en"),
        "favourites": data.get("favourites", []),
        "read_items": data.get("read_items", []),
        "bookmarked_items": data.get("bookmarked_items", []),
        "user_dir": data.get("user_dir", ""),
        "caching_enabled": data.get("caching_enabled", True),
        "update_interval": data.get("update_interval", 30),
        "categories": categories,
        "blacklist": data.get("blacklist", []),
    }


def parse_categories(data: list[dict[str, Any]]) -> list[Category]:
    """Parse categories list."""
    categories: list[Category] = []
    for cat_data in data:
        categories.append({
            "name": cat_data.get("name", ""),
            "icon": cat_data.get("icon", ""),
            "bind_patterns": cat_data.get("bind_patterns", []),
            "is_default": cat_data.get("is_default", False),
        })
    return categories


def parse_feeds(data: list[dict[str, Any]]) -> list[Feed]:
    """Parse feeds list."""
    feeds: list[Feed] = []
    for feed_data in data:
        # Parse items
        items = parse_items(feed_data.get("items", []))

        feeds.append({
            "link": feed_data.get("link", ""),
            "category": feed_data.get("category", ""),
            "language": feed_data.get("language", ""),
            "items": items,
        })
    return feeds


def parse_items(data: list[dict[str, Any]]) -> list[Item]:
    """Parse items list."""
    items: list[Item] = []
    for item_data in data:
        items.append({
            "guid": item_data.get("guid", ""),
            "title": item_data.get("title", ""),
            "link": item_data.get("link", ""),
            "description": item_data.get("description", ""),
            "pub_date": item_data.get("pub_date", ""),
            "categories": item_data.get("categories", []),
            "is_read": item_data.get("is_read", False),
            "is_bookmarked": item_data.get("is_bookmarked", False),
        })
    return items
