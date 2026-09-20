#File that parses a feed

import logging
import uuid as uuid_module
import xml.etree.ElementTree as ET
from typing import Any

from src.parser.atom_structs import AtomCategory, AtomEntry, AtomFeed, AtomLink, AtomPerson
from src.parser.rss_structs import RSSCategory, RSSChannel, RSSEnclosure, RSSImage, RSSItem

logger = logging.getLogger(__name__)

def parsefeed(tree: ET.ElementTree, feed_type: str, path: str) -> dict[str, Any]:
    """
    Main parser entry point. Routes to RSS or Atom parser based on feed_type.

    Args:
        tree: Parsed XML ElementTree
        feed_type: String indicating feed type (e.g., "RSS_2_0", "Atom_1_0")
        path: File path for logging/reference

    Returns:
        FeedData dict containing parsed feed data
    """
    logger.info(f"Parser called with feed type: {feed_type} from {path}")

    # Check if it's RSS
    if feed_type in ("RSS_0_90", "RSS_0_91", "RSS_0_92", "RSS_1_0", "RSS_2_0"):
        logger.info("Feed is RSS type. Parsing channel.")
        channel = parse_rss_channel(tree, path)
        return {
            "rss": channel,
            "feed_type": "RSS",
        }

    # Check if it's Atom
    elif feed_type in ("Atom_0_3", "Atom_1_0"):
        logger.info("Feed is Atom type. Parsing entries.")
        feed = parse_atom_feed(tree, path)
        return {
            "atom": feed,
            "feed_type": "Atom",
        }

    # Unknown type
    else:
        logger.error(f"Unknown feed type for parsing: {feed_type}")
        return {
            "feed_type": "Unknown",
        }


# ============================================================
# RSS PARSER
# ============================================================

def parse_rss_channel(tree: ET.ElementTree, path: str) -> RSSChannel:
    """
    Parse an RSS channel from the XML tree.

    Args:
        tree: Parsed XML ElementTree
        path: File path for logging

    Returns:
        RSSChannel dict containing channel data
    """
    root = tree.getroot()
    channel: RSSChannel = {
        "version": root.attrib.get("version", "2.0"),
        "feed_type": "RSS",
        "title": "",
        "link": "",
        "description": "",
        "language": "",
        "last_build_date": "",
        "pub_date": "",
        "generator": "",
        "copyright": "",
        "docs": "",
        "managing_editor": "",
        "web_master": "",
        "categories": [],
        "image": None,
        "items": [],
    }

    # Find channel element
    channel_elem = root.find("channel")
    if channel_elem is None:
        logger.error(f"No channel found in RSS feed: {path}")
        return channel

    # Required fields
    channel["title"] = get_text(channel_elem, "title")
    channel["link"] = get_text(channel_elem, "link")
    channel["description"] = get_text(channel_elem, "description")

    # Optional fields
    channel["language"] = get_text(channel_elem, "language")
    channel["copyright"] = get_text(channel_elem, "copyright")
    channel["generator"] = get_text(channel_elem, "generator")
    channel["managing_editor"] = get_text(channel_elem, "managingEditor")
    channel["web_master"] = get_text(channel_elem, "webMaster")
    channel["docs"] = get_text(channel_elem, "docs")

    # Dates (as strings, no parsing)
    channel["last_build_date"] = get_text(channel_elem, "lastBuildDate")
    channel["pub_date"] = get_text(channel_elem, "pubDate")

    # Parse categories
    channel["categories"] = parse_rss_categories(channel_elem)

    # Parse image
    channel["image"] = parse_image(channel_elem)

    # Parse items
    channel["items"] = parse_rss_items(channel_elem)

    logger.info(f"Finished parsing channel: {channel['title']}")
    return channel


def parse_image(parent: ET.Element) -> RSSImage | None:
    """
    Parse RSS image element.

    Args:
        parent: Parent element (channel)

    Returns:
        RSSImage dict or None if not found
    """
    image_elem = parent.find("image")
    if image_elem is None:
        return None

    img: RSSImage = {
        "url": get_text(image_elem, "url"),
        "title": get_text(image_elem, "title"),
        "link": get_text(image_elem, "link"),
        "description": get_text(image_elem, "description"),
        "width": 88,   # RSS default
        "height": 31,  # RSS default
    }

    # Parse width and height (with defaults)
    if width_str := get_text(image_elem, "width"):
        try:
            img["width"] = int(width_str)
        except ValueError:
            pass  # Keep default

    if height_str := get_text(image_elem, "height"):
        try:
            img["height"] = int(height_str)
        except ValueError:
            pass  # Keep default

    return img


def parse_rss_categories(parent: ET.Element) -> list[RSSCategory]:
    """
    Parse RSS category elements.

    Args:
        parent: Parent element (channel or item)

    Returns:
        List of RSSCategory dicts
    """
    categories: list[RSSCategory] = []

    for cat_elem in parent.findall("category"):
        categories.append({
            "name": cat_elem.text.strip() if cat_elem.text else "",
            "domain": cat_elem.attrib.get("domain", ""),
        })

    return categories


def parse_rss_items(parent: ET.Element) -> list[RSSItem]:
    """
    Parse all RSS items.

    Args:
        parent: Parent element (channel)

    Returns:
        List of RSSItem dicts
    """
    items: list[RSSItem] = []

    for item_elem in parent.findall("item"):
        item = parse_single_rss_item(item_elem)
        items.append(item)

    return items


def parse_single_rss_item(item_elem: ET.Element) -> RSSItem:
    """
    Parse a single RSS item.

    Args:
        item_elem: XML element for the item

    Returns:
        RSSItem dict with generated GUID if missing
    """
    # Get RSS guid if it exists
    rss_guid = get_text(item_elem, "guid")

    # If no GUID exists, generate a UUID v4
    final_guid = rss_guid
    if not final_guid:
        # Generate a UUID v4
        generated_uuid = uuid_module.uuid4()
        final_guid = str(generated_uuid)

    item: RSSItem = {
        "title": get_text(item_elem, "title"),
        "link": get_text(item_elem, "link"),
        "description": get_text(item_elem, "description"),
        "pub_date": get_text(item_elem, "pubDate"),
        "guid": final_guid,  # Use RSS guid if present, otherwise generated
        "author": get_text(item_elem, "author"),
        "comments": get_text(item_elem, "comments"),
        "content_encoded": get_text(item_elem, "content:encoded"),
        "source": get_text(item_elem, "source"),
        "categories": parse_rss_categories(item_elem),
        "enclosure": parse_rss_enclosure(item_elem),
    }

    return item


def parse_rss_enclosure(parent: ET.Element) -> RSSEnclosure | None:
    """
    Parse RSS enclosure (for podcasts/media).

    Args:
        parent: Parent element (item)

    Returns:
        RSSEnclosure dict or None if not found
    """
    enclosure_elem = parent.find("enclosure")
    if enclosure_elem is None:
        return None

    enc: RSSEnclosure = {
        "url": enclosure_elem.attrib.get("url", ""),
        "type": enclosure_elem.attrib.get("type", ""),
        "length": 0,
    }

    if length_str := enclosure_elem.attrib.get("length", ""):
        try:
            enc["length"] = int(length_str)
        except ValueError:
            pass  # Keep default 0

    return enc


# ============================================================
# ATOM PARSER
# ============================================================

# Atom namespace (used for all Atom tags)
ATOM_NS = "{http://www.w3.org/2005/Atom}"


def parse_atom_feed(tree: ET.ElementTree, path: str) -> AtomFeed:
    """
    Parse an Atom feed from the XML tree.

    Args:
        tree: Parsed XML ElementTree
        path: File path for logging

    Returns:
        AtomFeed dict containing feed data
    """
    logger.info(f"Parsing Atom feed from {path}")

    root = tree.getroot()
    feed: AtomFeed = {
        "feed_type": "Atom",
        "title": "",
        "id": "",
        "updated": "",
        "link": {
            "href": "",
            "rel": "",
            "type": "",
            "hreflang": "",
            "title": "",
            "length": 0,
        },
        "subtitle": "",
        "author": [],
        "icon": "",
        "logo": "",
        "rights": "",
        "generator": "",
        "categories": [],
        "entries": [],
    }

    # Atom feed elements are direct children of the root
    feed["title"] = get_text(root, f"{ATOM_NS}title")
    feed["id"] = get_text(root, f"{ATOM_NS}id")
    feed["updated"] = get_text(root, f"{ATOM_NS}updated")
    feed["subtitle"] = get_text(root, f"{ATOM_NS}subtitle")
    feed["rights"] = get_text(root, f"{ATOM_NS}rights")
    feed["generator"] = get_text(root, f"{ATOM_NS}generator")
    feed["icon"] = get_text(root, f"{ATOM_NS}icon")
    feed["logo"] = get_text(root, f"{ATOM_NS}logo")

    # Parse authors
    feed["author"] = parse_atom_persons(root, "author")

    # Parse categories
    feed["categories"] = parse_atom_categories(root)

    # Parse links
    feed["link"] = parse_atom_link(root)

    # Parse entries
    feed["entries"] = parse_atom_entries(root)

    logger.info(f"Finished parsing Atom feed: {feed['title']}")
    return feed


def parse_atom_persons(parent: ET.Element, tag: str) -> list[AtomPerson]:
    """
    Parse Atom person elements (author, contributor).

    Args:
        parent: Parent element
        tag: Tag name (e.g., "author", "contributor")

    Returns:
        List of AtomPerson dicts
    """
    persons: list[AtomPerson] = []

    for person_elem in parent.findall(f"{ATOM_NS}{tag}"):
        persons.append({
            "name": get_text(person_elem, f"{ATOM_NS}name"),
            "email": get_text(person_elem, f"{ATOM_NS}email"),
            "uri": get_text(person_elem, f"{ATOM_NS}uri"),
        })

    return persons


def parse_atom_categories(parent: ET.Element) -> list[AtomCategory]:
    """
    Parse Atom category elements.

    Args:
        parent: Parent element

    Returns:
        List of AtomCategory dicts
    """
    categories: list[AtomCategory] = []

    for cat_elem in parent.findall(f"{ATOM_NS}category"):
        categories.append({
            "term": cat_elem.attrib.get("term", ""),
            "scheme": cat_elem.attrib.get("scheme", ""),
            "label": cat_elem.attrib.get("label", ""),
        })

    return categories


def parse_atom_link(parent: ET.Element) -> AtomLink:
    """
    Parse the main Atom link (rel="alternate").

    Args:
        parent: Parent element (feed)

    Returns:
        AtomLink dict
    """
    # Find the link with rel="alternate"
    for link_elem in parent.findall(f"{ATOM_NS}link"):
        rel = link_elem.attrib.get("rel", "")
        if rel == "alternate" or not rel:
            return {
                "href": link_elem.attrib.get("href", ""),
                "rel": rel,
                "type": link_elem.attrib.get("type", ""),
                "hreflang": link_elem.attrib.get("hreflang", ""),
                "title": link_elem.attrib.get("title", ""),
                "length": parse_length_attr(link_elem.attrib.get("length", "")),
            }

    # No alternate link found
    return {
        "href": "",
        "rel": "",
        "type": "",
        "hreflang": "",
        "title": "",
        "length": 0,
    }


def parse_atom_entries(parent: ET.Element) -> list[AtomEntry]:
    """
    Parse Atom entries.

    Args:
        parent: Parent element (feed)

    Returns:
        List of AtomEntry dicts
    """
    entries: list[AtomEntry] = []

    for entry_elem in parent.findall(f"{ATOM_NS}entry"):
        entry = parse_single_atom_entry(entry_elem)
        entries.append(entry)

    return entries


def parse_single_atom_entry(entry_elem: ET.Element) -> AtomEntry:
    """
    Parse a single Atom entry.

    Args:
        entry_elem: XML element for the entry

    Returns:
        AtomEntry dict
    """
    entry: AtomEntry = {
        "title": get_text(entry_elem, f"{ATOM_NS}title"),
        "id": get_text(entry_elem, f"{ATOM_NS}id"),
        "updated": get_text(entry_elem, f"{ATOM_NS}updated"),
        "published": get_text(entry_elem, f"{ATOM_NS}published"),
        "summary": get_text(entry_elem, f"{ATOM_NS}summary"),
        "content": get_text(entry_elem, f"{ATOM_NS}content"),
        "link": parse_atom_entry_link(entry_elem),
        "author": parse_atom_persons(entry_elem, "author"),
        "categories": parse_atom_categories(entry_elem),
        "source": None,  # Optional, parsed below
        "is_read": False,
        "is_starred": False,
    }

    # Parse source (optional)
    source_elem = entry_elem.find(f"{ATOM_NS}source")
    if source_elem is not None:
        # Parse source as a feed (recursive)
        # For simplicity, we parse the source element directly
        entry["source"] = {
            "feed_type": "Atom",
            "title": get_text(source_elem, f"{ATOM_NS}title"),
            "id": get_text(source_elem, f"{ATOM_NS}id"),
            "updated": get_text(source_elem, f"{ATOM_NS}updated"),
            "link": parse_atom_link(source_elem),
            "subtitle": get_text(source_elem, f"{ATOM_NS}subtitle"),
            "author": parse_atom_persons(source_elem, "author"),
            "icon": get_text(source_elem, f"{ATOM_NS}icon"),
            "logo": get_text(source_elem, f"{ATOM_NS}logo"),
            "rights": get_text(source_elem, f"{ATOM_NS}rights"),
            "generator": get_text(source_elem, f"{ATOM_NS}generator"),
            "categories": parse_atom_categories(source_elem),
            "entries": [],  # Source feeds don't typically have entries
        }

    return entry


def parse_atom_entry_link(parent: ET.Element) -> AtomLink:
    """
    Parse link for an entry (find the alternate link).

    Args:
        parent: Parent element (entry)

    Returns:
        AtomLink dict
    """
    for link_elem in parent.findall(f"{ATOM_NS}link"):
        rel = link_elem.attrib.get("rel", "")
        if rel == "alternate" or not rel:
            return {
                "href": link_elem.attrib.get("href", ""),
                "rel": rel,
                "type": link_elem.attrib.get("type", ""),
                "hreflang": link_elem.attrib.get("hreflang", ""),
                "title": link_elem.attrib.get("title", ""),
                "length": parse_length_attr(link_elem.attrib.get("length", "")),
            }

    # No alternate link found
    return {
        "href": "",
        "rel": "",
        "type": "",
        "hreflang": "",
        "title": "",
        "length": 0,
    }


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def get_text(parent: ET.Element, tag: str) -> str:
    """
    Safely get text content from a child element.

    Args:
        parent: Parent element
        tag: Tag name (may include namespace prefix)

    Returns:
        Text content or empty string
    """
    elem = parent.find(tag)
    if elem is not None and elem.text:
        return elem.text.strip()
    return ""


def parse_length_attr(length_str: str) -> int:
    """
    Parse length attribute from string.

    Args:
        length_str: Length string (e.g., "1337")

    Returns:
        Integer length or 0 if invalid
    """
    if not length_str:
        return 0
    try:
        return int(length_str)
    except ValueError:
        return 0
