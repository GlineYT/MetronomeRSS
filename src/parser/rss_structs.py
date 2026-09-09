from typing import TypedDict

# ============================================================
# RSS STRUCTS (Python TypedDict version)
# ============================================================

class RSSImage(TypedDict):
    """RSS Image (nested struct)"""
    url: str          # Required
    title: str        # Required
    link: str         # Required
    description: str  # Optional (default: "")
    width: int        # Optional (default: 88)
    height: int       # Optional (default: 31)


class RSSCategory(TypedDict):
    """RSS Category (with optional domain)"""
    name: str
    domain: str       # Optional (default: "")


class RSSEnclosure(TypedDict):
    """RSS Enclosure (for podcasts/media)"""
    url: str
    length: int       # In bytes
    type: str         # MIME type, e.g., "audio/mpeg"


class RSSItem(TypedDict):
    """RSS Item"""
    # Required
    title: str
    link: str

    # Recommended
    description: str
    pub_date: str

    # Optional
    guid: str
    author: str
    comments: str
    categories: list[RSSCategory]

    # Extensions
    content_encoded: str
    enclosure: RSSEnclosure | None

    # Metadata
    source: str


class RSSChannel(TypedDict):
    """RSS Channel (RSS 0.90, 0.91, 0.92, 2.0 compatible)"""
    # Required
    title: str
    link: str
    description: str

    # Recommended / Common
    language: str
    last_build_date: str
    pub_date: str
    generator: str
    copyright: str
    docs: str

    # Contact Info
    managing_editor: str
    web_master: str

    # Category
    categories: list[RSSCategory]

    # Image
    image: RSSImage | None

    # Items
    items: list[RSSItem]

    # Metadata
    version: str
    feed_type: str
