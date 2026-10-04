import logging

import src.parser.feed_loader as feed_loader
import src.parser.feed_parser as feed_parser
import src.parser.feed_post_processor as feed_post_processor
import src.parser.feed_validator as feed_validator

logger = logging.getLogger(__name__)


def init_pipeline(path):
    # --- Load the file ---
    logger.info("Attempting to load RSS/Atom feed")
    RSStree, error = feed_loader.loadXML(path)

    # Bail out if loading failed
    if error != "INF_ALL_OK" or RSStree is None:
        logger.error(f"Failed to load feed: {error}")
        return None

    # --- Validate the feed type ---
    feedType, valid, error = feed_validator.validateFeedType(RSStree, path)
    logger.info(f"Validation finished with returns: ({feedType},{valid!s},{error})")

    if not valid:
        logger.error(f"Feed type validation failed: {error}")
        return None

    # --- Validate the fields ---
    valid, error = feed_validator.validateFields(RSStree, feedType, path)
    logger.info(f"Field validation finished with results ({valid},{error})")

    if not valid:
        logger.error(f"Field validation failed: {error}")
        return None

    # --- Parse ---
    ParsedFeed = feed_parser.parsefeed(RSStree, feedType, path)

    # --- Post-process ---
    logger.info("Beginning post processing")
    ParsedFeed = feed_post_processor.recursive_unescape(ParsedFeed)
    print(f"Processed feed {ParsedFeed}")

    return ParsedFeed
