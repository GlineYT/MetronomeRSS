"""
Feed loading, caching, and extraction logic.

This module is UI-agnostic. It deals with files, downloads, and parsing.
It does NOT import pygame or any UI code.
"""
import logging
from pathlib import Path

from src.parser import pipeline
from src.util import strip_html
from src.util import date_parser
from src.net import downloader
from src.user import config_crud

logger = logging.getLogger(__name__)


def parse_feed(path):
    """Parse a feed file via the pipeline."""
    logger.info(f"Parsing feed: {path}")
    return pipeline.init_pipeline(path)


def extract_items(parsed_feed):
    """Extract (title, description, metadata_dict) tuples from a parsed feed."""
    items = []
    if not parsed_feed:
        return items

    if parsed_feed.get("feed_type") == "RSS" and "rss" in parsed_feed:
        channel = parsed_feed["rss"]
        channel_title = channel.get("title", "Unknown source")
        for item in channel.get("items", []):
            title = item.get("title", "Untitled")
            description = strip_html._strip_html(item.get("description", ""))
            pub_date = item.get("pub_date", "")

            date_str, time_str = date_parser.parse_feed_date(pub_date)

            metadata = {
                "source": channel_title,
                "link": item.get("link", ""),
                "time": time_str,
                "date": date_str,
            }
            items.append((title, description, metadata))
    return items


def load_feeds(profile_path, tmp_dir):
    """
    Load and parse all saved feeds from the given profile.

    Args:
        profile_path: Path to the profile JSON.
        tmp_dir: Directory where feeds are cached.

    Returns:
        (items, feed_count):
        - items: list of (title, description, metadata)
        - feed_count: number of feeds processed
    """
    if not profile_path:
        logger.warning("No profile path — cannot load feeds")
        return [], 0

    feeds = config_crud.update_user_data(profile_path, "feeds", "read")
    if not feeds:
        logger.info("No saved feeds")
        return [], 0

    tmp_dir = Path(tmp_dir)
    all_items = []

    for feed_entry in feeds:
        url = feed_entry.get("link") if isinstance(feed_entry, dict) else feed_entry
        if not url:
            continue

        filename = downloader.url_to_filename(url)
        cached = tmp_dir / filename

        if cached.exists():
            logger.info(f"Using cached feed: {cached}")
            parsed = parse_feed(str(cached))
        else:
            logger.info(f"No cache for {url} — downloading")
            paths, error = downloader.downloadRSS([url], destination=tmp_dir)
            if error != downloader.INF_DL_ALL_OK or not paths:
                logger.error(f"Failed to download {url}: {error}")
                continue
            parsed = parse_feed(paths[0])

        if parsed is None:
            logger.error(f"Failed to parse feed: {url}")
            continue

        all_items.extend(extract_items(parsed))

    logger.info(f"Loaded {len(all_items)} items from {len(feeds)} feeds")
    return all_items, len(feeds)


def reload_feeds(profile_path, tmp_dir):
    """Force a fresh download by deleting cached files, then loading."""
    if not profile_path:
        return [], 0

    feeds = config_crud.update_user_data(profile_path, "feeds", "read")
    if not feeds:
        return [], 0

    tmp_dir = Path(tmp_dir)
    for feed_entry in feeds:
        url = feed_entry.get("link") if isinstance(feed_entry, dict) else feed_entry
        if not url:
            continue
        cached = tmp_dir / downloader.url_to_filename(url)
        if cached.exists():
            logger.info(f"Deleting cache: {cached}")
            cached.unlink()

    return load_feeds(profile_path, tmp_dir)
