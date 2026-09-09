"""
Configuration TypedDict Definitions
"""
from typing import TypedDict, List, Optional

class Color(TypedDict):
    """RGB color object."""
    r: int
    g: int
    b: int


class Category(TypedDict):
    """User-defined category."""
    name: str
    icon: str
    bind_patterns: List[str]
    is_default: bool


class Item(TypedDict):
    """Feed item/article."""
    guid: str
    title: str
    link: str
    description: str
    pub_date: str
    categories: List[str]
    is_read: bool
    is_bookmarked: bool


class Feed(TypedDict):
    """Subscribed feed."""
    link: str
    category: str
    language: str
    items: List[Item]


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
    favourites: List[str]
    read_items: List[str]
    bookmarked_items: List[str]
    user_dir: str
    caching_enabled: bool
    update_interval: int
    categories: List[Category]
    blacklist: List[str]


class Profile(TypedDict):
    """Complete user profile."""
    metadata: Metadata
    preferences: Preferences
    feeds: List[Feed]
