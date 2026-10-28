import threading
import queue
import logging
from pathlib import Path

from src.net import downloader
from src.user import config_crud
from src.ui.functions import feeds  # Needed for the reload worker

logger = logging.getLogger(__name__)

# --- Thread-safe queues for results ---
_download_queue = queue.Queue()
_reload_queue = queue.Queue()


def start_download_async(url, tmp_dir, save_to_profile=None):
    """
    Start downloading a feed in a background thread.
    When done, the result is pushed to _download_queue.
    """
    def _worker():
        try:
            # The actual blocking network call
            paths, error = downloader.downloadRSS([url], destination=tmp_dir)

            if error == downloader.INF_DL_ALL_OK and save_to_profile:
                logger.info(f"Saving url to profile: {url}")
                config_crud.add_feed_to_profile(save_to_profile, url)

            _download_queue.put(("done", paths, error))
        except Exception as e:
            logger.exception("Download thread crashed")
            _download_queue.put(("error", [], str(e)))

    thread = threading.Thread(target=_worker, daemon=True)
    thread.start()
    logger.info(f"Started background download for: {url}")


def poll_download_result():
    """
    Check if a background download has finished.
    Call this every frame in the Pygame main loop.
    """
    try:
        return _download_queue.get_nowait()
    except queue.Empty:
        return None


def start_reload_async(profile_path, tmp_dir):
    """
    Start reloading all feeds in a background thread.
    When done, the result is pushed to _reload_queue.
    """
    def _worker():
        try:
            # This calls the function we wrote earlier that deletes cache and re-downloads
            items, count = feeds.reload_feeds(profile_path, tmp_dir)
            _reload_queue.put(("done", items, count))
        except Exception as e:
            logger.exception("Reload thread crashed")
            _reload_queue.put(("error", [], 0))

    thread = threading.Thread(target=_worker, daemon=True)
    thread.start()
    logger.info("Started background reload")


def poll_reload_result():
    """
    Check if a background reload has finished.
    Call this every frame in the Pygame main loop.
    """
    try:
        return _reload_queue.get_nowait()
    except queue.Empty:
        return None
