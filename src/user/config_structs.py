"""
Configuration TypedDict Definitions
"""
from typing import TypedDict


class Color(TypedDict):
    """RGB color object."""
    r: int
    g: int
    b: int


class Category(TypedDict):
    """User-defined category."""
    name: str
    icon: str
    bind_patterns: list[str]
    is_default: bool


class Item(TypedDict):
    """Feed item/article."""
    guid: str
    title: str
    link: str
    description: str
    pub_date: str
    categories: list[str]
    is_read: bool
    is_bookmarked: bool


class Feed(TypedDict):
    """Subscribed feed."""
    link: str
    category: str
    language: str
    items: list[Item]


class Metadata(TypedDict):
    """Profile metadata."""
    guid: str
    created_date: str
    created_time: str
    modified_date: str
    modified_time: str


class Preferences(TypedDict):
    """User preferences."""
    color_theme: Color
    language: str
    favourites: list[str]
    read_items: list[str]
    bookmarked_items: list[str]
    user_dir: str
    caching_enabled: bool
    update_interval: int
    categories: list[Category]
    blacklist: list[str]


class Profile(TypedDict):
    """Complete user profile."""
    metadata: Metadata
    preferences: Preferences
    feeds: list[Feed]
