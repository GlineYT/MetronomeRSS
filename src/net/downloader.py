import logging
import os
import tempfile
import socket

from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import urlretrieve

logger = logging.getLogger(__name__)

socket.setdefaulttimeout(30)  # 30 second timeout for all socket (in this case network) operations

# --- Error codes ---
ERR_URL_INVALID = "ERR_URL_INVALID"
ERR_DL_FAILED = "ERR_DL_FAILED"
ERR_DL_HTTP = "ERR_DL_HTTP"
ERR_DL_NETWORK = "ERR_DL_NETWORK"
ERR_DL_DEST = "ERR_DL_DEST"
INF_DL_ALL_OK = "INF_DL_ALL_OK"


def downloadRSS(urllist, destination=None):
    """
    Downloads a list of RSS files from given URLs.

    Args:
        urllist: List of URLs to download.
        destination: Optional directory to save files into.
                     Defaults to the user's temp folder.

    Returns:
        (file_paths, error_code)
        - file_paths: List of paths to successfully downloaded files.
        - error_code: INF_DL_ALL_OK on full success, otherwise the
                      last error code that occurred.
    """
    # --- Resolve destination ---
    if destination is None:
        destination = tempfile.gettempdir()
        logger.info(f"No destination given, defaulting to: {destination}")

    dest_path = Path(destination).resolve()

    # --- Ensure destination exists ---
    try:
        dest_path.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        logger.error(f"Could not create destination directory {dest_path}: {e}")
        return [], ERR_DL_DEST

    file_paths = []
    last_error = INF_DL_ALL_OK

    # --- Iterate over the URL list ---
    for url in urllist:
        # --- Basic URL sanity check ---
        if not isinstance(url, str) or not url.strip():
            logger.error(f"Invalid URL: {url!r}")
            last_error = ERR_URL_INVALID
            continue

        # --- Derive a filename from the URL ---
        filename = os.path.basename(url.split("?")[0]) or "feed.xml"
        target = dest_path / filename

        logger.info(f"Downloading: {url} -> {target}")

        # --- Attempt the download ---
        try:
            urlretrieve(url, str(target))
            file_paths.append(str(target))
            logger.info(f"Downloaded successfully: {target}")

        except HTTPError as e:
            logger.error(f"HTTP error downloading {url}: {e.code} {e.reason}")
            last_error = ERR_DL_HTTP

        except URLError as e:
            logger.error(f"Network error downloading {url}: {e.reason}")
            last_error = ERR_DL_NETWORK

        except OSError as e:
            logger.error(f"Filesystem error saving {url} to {target}: {e}")
            last_error = ERR_DL_DEST

        except Exception as e:  # noqa: BLE001
            logger.exception(f"Unexpected error downloading {url}: {e}")
            last_error = ERR_DL_FAILED

    logger.info(f"Download complete: {len(file_paths)}/{len(urllist)} succeeded")
    return file_paths, last_error
