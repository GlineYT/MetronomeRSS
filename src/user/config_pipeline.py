"""
Configuration Processing Pipeline
Loads, validates, and parses the user profile configuration.
"""
import logging
from typing import Tuple, Optional

import src.user.config_loader as config_loader
import src.user.config_validator as config_validator
import src.user.config_parser as config_parser
from src.user.config_structs import Profile

logger = logging.getLogger(__name__)

def load_profile(config_path: Optional[str] = None) -> Tuple[Optional[Profile], Optional[str]]:
    """
    Complete configuration pipeline.

    Args:
        config_path: Path to the config file (uses default if None)

    Returns:
        Tuple of (profile, error_code)
        - profile: Profile object or None on failure
        - error_code: Error code string or None on success
    """
    # Use default path if not provided
    if config_path is None:
        config_path = config_loader.get_default_config_path()

    logger.info(f"Loading profile from: {config_path}")

    # Stage 1: Load
    data, load_error = config_loader.load_config(config_path)
    if load_error is not None:
        logger.error(f"Failed to load config: {load_error}")
        return None, load_error

    # Stage 2: Validate
    valid, validation_error = config_validator.validate_config(data)
    if not valid:
        logger.error(f"Failed to validate config: {validation_error}")
        return None, validation_error

    # Stage 3: Parse
    profile = config_parser.parse_config(data)
    if profile is None:
        logger.error("Failed to parse config")
        return None, "ERR_PARSE_CONFIG"

    logger.info("Profile loaded successfully")
    print(profile )
    return profile, None



