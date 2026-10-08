"""
Network operations triggered by the UI.

This module handles the download-then-maybe-save flow.
"""
import logging
from pathlib import Path

from src.net import downloader
from src.user import config_crud

logger = logging.getLogger(__name__)


def perform_download(url, tmp_dir, save_to_profile=None):
    """
    Download a feed and optionally save its URL to a profile.

    Args:
        url: Feed URL.
        tmp_dir: Directory to download into.
        save_to_profile: Optional profile path. If set, the URL is added
                         to the profile's feeds list.

    Returns:
        (paths, error_code) — from downloadRSS.
    """
    logger.info(f"Downloading feed: {url}")
    tmp_dir = Path(tmp_dir)
    paths, error_code = downloader.downloadRSS([url], destination=tmp_dir)

    if error_code != downloader.INF_DL_ALL_OK or not paths:
        logger.error(f"Download failed: {error_code}")
        return paths, error_code

    logger.info(f"Downloaded: {paths[0]}")

    if save_to_profile:
        logger.info(f"Saving url to profile: {url}")
        config_crud.add_feed_to_profile(save_to_profile, url)

    return paths, error_code
