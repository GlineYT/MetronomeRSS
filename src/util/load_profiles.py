import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def load_profiles_from_directory(directory: Path):
    """
    Scan the given directory for JSON files, load them, and extract:
    - Profile name from filename
    - Color theme from preferences.color_theme
    """
    profiles = {}

    if not directory.exists():
        logger.warning(f"Profile directory does not exist: {directory}")
        return profiles

    # Find all .json files
    json_files = list(directory.glob("*.json"))

    if not json_files:
        logger.warning(f"No JSON files found in {directory}")
        return profiles

    for json_path in json_files:
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Extract the profile name from the filename (without extension)
            profile_name = json_path.stem  # e.g., "profile1"

            # Extract color theme
            color = data.get("preferences", {}).get("color_theme", {})
            r = color.get("r", 30)
            g = color.get("g", 144)
            b = color.get("b", 255)

            # Convert to hex string for pygame
            color_hex = f"#{r:02x}{g:02x}{b:02x}"

            # Store the profile info (you can store more data later if needed)
            profiles[profile_name] = {
                "color_hex": color_hex,
                "file_path": json_path,
                "data": data
            }

            logger.info(f"Loaded profile: {profile_name} with color {color_hex}")

        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in {json_path}: {e}")

    return profiles
