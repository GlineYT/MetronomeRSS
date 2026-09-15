"""
Stage 1: Configuration Loader
Loads and validates the profile.json file.
"""
import json
import logging
import os
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# Error codes
ERR_CONFIG_NOT_FOUND = "ERR_CONFIG_NOT_FOUND"
ERR_CONFIG_INVALID_JSON = "ERR_CONFIG_INVALID_JSON"
ERR_CONFIG_EMPTY = "ERR_CONFIG_EMPTY"
ERR_CONFIG_PERMISSION = "ERR_CONFIG_PERMISSION"


def load_config(config_path: str) -> tuple[dict[str, Any] | None, str | None]:
    """
    Stage 1: Load the profile.json file.

    Args:
        config_path: Path to the profile.json file

    Returns:
        Tuple of (config_dict, error_code)
        - config_dict: Parsed JSON data or None on failure
        - error_code: Error code string or None on success
    """
    logger.info(f"Loading config from: {config_path}")

    # Check if file exists
    if not os.path.exists(config_path):
        logger.error(f"Config file not found: {config_path}")
        return None, ERR_CONFIG_NOT_FOUND

    # Check if file is readable
    if not os.access(config_path, os.R_OK):
        logger.error(f"Config file not readable: {config_path}")
        return None, ERR_CONFIG_PERMISSION

    # Check if file is empty
    if os.path.getsize(config_path) == 0:
        logger.error(f"Config file is empty: {config_path}")
        return None, ERR_CONFIG_EMPTY

    # Try to parse JSON
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in config file: {e}")
        return None, ERR_CONFIG_INVALID_JSON
    except UnicodeDecodeError as e:
        logger.error(f"File is not valid UTF-8: {e}")
        return None, ERR_CONFIG_INVALID_JSON
    except OSError as e:
        logger.error(f"Failed to read config file: {e}")
        return None, ERR_CONFIG_PERMISSION

    # Check if data is a dictionary
    if not isinstance(data, dict):
        logger.error("Config root is not a dictionary")
        return None, ERR_CONFIG_INVALID_JSON

    logger.info("Config loaded successfully")
    return data, None


def get_default_config_path() -> str:
    """
    Get the default configuration file path.

    Returns:
        Default path to profile.json
    """
    home = Path.home()
    default_dir = home / "MetronomeRSS" / "Profiles" / "Default"
    return str(default_dir / "profile.json")


def ensure_config_directory(config_path: str) -> bool:
    """
    Ensure the config directory exists.

    Args:
        config_path: Path to the config file

    Returns:
        True if directory exists or was created, False on error
    """
    try:
        Path(config_path).parent.mkdir(parents=True, exist_ok=True)
        return True
    except OSError as e:
        logger.error(f"Failed to create config directory: {e}")
        return False
