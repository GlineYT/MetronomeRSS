from typing import TypedDict, List, Optional

# ============================================================
# ATOM STRUCTS (Python TypedDict version)
# ============================================================

class AtomPerson(TypedDict):
    """Atom Person (author/contributor)"""
    name: str          # Required
    email: str         # Optional
    uri: str           # Optional


class AtomLink(TypedDict):
    """Atom Link"""
    href: str          # Required
    rel: str           # Optional
    type: str          # Optional
    hreflang: str      # Optional
    title: str         # Optional
    length: int        # Optional


class AtomCategory(TypedDict):
    """Atom Category"""
    term: str          # Required
    scheme: str        # Optional
    label: str         # Optional


class AtomEntry(TypedDict):
    """Atom Entry (equivalent to RSS item)"""
    # Required
    title: str
    id: str
    updated: str
    link: AtomLink

    # Recommended
    published: str
    summary: str
    content: str
    author: List[AtomPerson]

    # Optional
    categories: List[AtomCategory]
    source: Optional['AtomFeed']  # Self-referential type

    # Reader State
    is_read: bool
    is_starred: bool


class AtomFeed(TypedDict):
    """Atom Feed"""
    # Required
    title: str
    id: str
    updated: str
    link: AtomLink

    # Recommended
    subtitle: str
    author: List[AtomPerson]
    icon: str
    logo: str
    rights: str
    generator: str

    # Optional
    categories: List[AtomCategory]
    entries: List[AtomEntry]

    # Metadata
    feed_type: str
