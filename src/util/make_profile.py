import json
import uuid
import random
import logging

from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)

def create_empty_profile(directory: str, name: str) -> str:
    """
    Create an empty profile file at the given directory with the given name.

    Args:
        directory: The directory where the profile file should be created.
        name: The name of the profile (used as the filename).

    Returns:
        The full path to the created profile file.
    """
    logger.info("Creating new profile")
    dir_path = Path(directory).resolve()
    dir_path.mkdir(parents=True, exist_ok=True)

    profile_path = dir_path / f"{name}.json"

    now = datetime.now()
    current_date = now.strftime("%Y-%m-%d")
    current_time = now.strftime("%H:%M:%S")

    profile = {
        "metadata": {
            "guid": str(uuid.uuid4()),
            "created_date": current_date,
            "created_time": current_time,
            "modified_date": current_date,
            "modified_time": current_time,
        },
        "preferences": {
            "color_theme": {"r": 255, "g": 128, "b": 0},
            "language": "en",
            "favourites": [],
            "read_items": [],
            "bookmarked_items": [],
            "user_dir": str(dir_path),
            "caching_enabled": True,
            "update_interval": 30,
            "categories": [],
            "blacklist": [],
        },
        "feeds": [],
    }

    with open(profile_path, "w", encoding="utf-8") as f:
        json.dump(profile, f, indent=4, ensure_ascii=False)

    logger.info("Profile created")
    return str(profile_path)


def generate_default_profile_name() -> str:
    """
    Generate a default profile name with a random 4-digit number.

    Returns:
        A string like "Default profile - 4821".
    """
    return f"Default profile - {random.randint(1000, 9999):04d}"
