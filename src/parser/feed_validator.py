#file that validates a feed
import logging

#Validates a RSS feed for validity.
logger = logging.getLogger(__name__)
#Namespace declaration

RDF_NS = "{http://www.w3.org/1999/02/22-rdf-syntax-ns#}"
RSS_1_0_NS = "{http://purl.org/rss/1.0/}"
RSS_1_0_NS_URL = "http://purl.org/rss/1.0/"
ATOM_NS = "{http://www.w3.org/2005/Atom}"


def validateFeedType(RSStree, path):
    logger.info(" Beginning feed validation")
    feedType = "Unknown"
    valid = False
    error = "ERR_UNK_FEED"

    root = RSStree.getroot()
    logger.info("Root element:" + root.tag)
    print(root.tag)

    # --- Check for RSS 1.0 (RDF) ---
    if root.tag == f"{RDF_NS}RDF":
        # Verify the channel uses the RSS 1.0 namespace
        if root.find(f"{RSS_1_0_NS}channel") is not None:
            logger.info(f"Valid RSS 1.0 (RDF) from file: {path}")
            return "RSS_1_0", True, "INF_ALL_OK"
        else:
            logger.error(f"RDF document has no RSS 1.0 channel (file: {path})")
            return "Unknown", False, "ERR_UNK_FEED"

    # --- RSS 0.90 / 0.91 / 0.92 / 2.0 ---
    if root.tag == "rss":
        version = root.attrib.get("version")
        if not version:
            logger.error(f"RSS feed has no version attribute (file: {path})")
            return "Unknown", False, "ERR_UNK_RSS"

        logger.info(f"RSS Feed version is: {version}")
        version_map = {
            "0.90": "RSS_0_90",
            "0.91": "RSS_0_91",
            "0.92": "RSS_0_92",
            "2.0": "RSS_2_0",
        }
        feedType = version_map.get(version)
        if feedType:
            logger.info(f"Valid {feedType} from file: {path}")
            return feedType, True, "INF_ALL_OK"
        else:
            logger.error(f"Unknown RSS version {version} in file: {path}")
            return "Unknown", False, "ERR_UNK_RSS"

    # --- Atom 1.0 ---
    if root.tag == f"{ATOM_NS}feed":
        logger.info(f"Valid Atom 1.0 from file: {path}")
        return "Atom_1_0", True, "INF_ALL_OK"

    # --- Unknown ---
    logger.error(f"Unknown feed type (root: {root.tag})")
    return "Unknown", False, "ERR_UNK_FEED"


def validateFields(RSStree, feedType, path):
    """
    Check for required fields in RSS/Atom feeds based on the feed type.

    Args:
        RSStree: The XML ElementTree parsed from the feed file
        feedType: String indicating the feed type (e.g., "RSS_2_0", "Atom_1_0")
        path: File path for logging/reference

    Returns:
        valid: Boolean indicating if all required fields are present
        error: String error code or "INF_ALL_OK" if successful
    """
    logger.info(f"Validating fields for feed from {path} of type {feedType}")

    root = RSStree.getroot()

    if feedType == "RSS_1_0":
        # RSS 1.0 uses the RSS 1.0 namespace
        RSS_1_0_NS_EL = "{http://purl.org/rss/1.0/}"

        channel = root.find(f"{RSS_1_0_NS_EL}channel")
        if channel is None:
            logger.error(f"No channel found in RDF/RSS 1.0 (file: {path})")
            return False, "ERR_NO_CNL"
        logger.info("Channel tag present.")

        if channel.find(f"{RSS_1_0_NS_EL}title") is None:
            logger.error(f"No <title> found in channel (file: {path})")
            return False, "ERR_NO_TTL"
        logger.info("Title tag present.")

        if channel.find(f"{RSS_1_0_NS_EL}link") is None:
            logger.error(f"No <link> found in channel (file: {path})")
            return False, "ERR_NO_LNK"
        logger.info("Link tag present.")

        if channel.find(f"{RSS_1_0_NS_EL}description") is None:
            logger.error(f"No <description> found in channel (file: {path})")
            return False, "ERR_NO_DSC"
        logger.info("Description tag present.")

        logger.info("All checks passed")
        return True, "INF_ALL_OK"

    # RSS FEEDS
    if feedType in ("RSS_0_90", "RSS_0_91", "RSS_0_92", "RSS_1_0", "RSS_2_0"):

        logger.info(f"Checking for channel in RSS feed from file: {path}")

        # Check for channel
        channel = root.find("channel")
        if channel is None:
            logger.error(f"No channel found in file: {path}")
            return False, "ERR_NO_CNL"
        else:
            logger.info("Channel tag present.")

        # Check for title
        if channel.find("title") is None:
            logger.error(f"No <title> found in channel (file: {path})")
            return False, "ERR_NO_TTL"
        else:
            logger.info("Title tag present.")

        # Check for description
        if channel.find("description") is None:
            logger.error(f"No <description> found in channel (file: {path})")
            return False, "ERR_NO_DSC"
        else:
            logger.info("Description tag present.")

        # Check for link
        if channel.find("link") is None:
            logger.error(f"No <link> found in channel (file: {path})")
            return False, "ERR_NO_LNK"
        else:
            logger.info("Link tag present.")

        # RSS 0.91 and 0.90 requires language
        if feedType in ("RSS_0_90", "RSS_0_91"):
            logger.info(f"{feedType} feed detected, checking for <language>")
            if channel.find("language") is None:
                logger.warning(f"{feedType} feed missing <language> (file: {path})")
                error = "WRN_NO_LNG"
            else:
                logger.info("Language tag present.")

        # RSS 1.0 requires RDF namespace
        if feedType == "RSS_1_0":
            logger.info("RSS 1.0 feed detected, checking for RDF namespace")
            rdf_ns = root.get("xmlns:rdf", "")
            if rdf_ns != "http://www.w3.org/1999/02/22-rdf-syntax-ns#":
                logger.error(f"RSS 1.0 feed missing or incorrect RDF namespace (file: {path})")
                return False, "ERR_NO_RDF"
            logger.info("RDF namespace present.")

        # All RSS checks passed
        logger.info("All checks passed")
        error = ""
        return True, error if error != "" else "INF_ALL_OK"

    # ATOM FEEDS
    elif feedType in ("Atom_0_3", "Atom_1_0"):
        logger.info(f"Checking Atom feed: {path}")

        # Atom requires: title, link, id, updated
        if root.find(f"{ATOM_NS}title") is None:
            logger.error(f"No <title> found in Atom feed (file: {path})")
            return False, "ERR_NO_TTL"
        else:
            logger.info("Title tag present.")

        if root.find(f"{ATOM_NS}link") is None:
            logger.error(f"No <link> found in Atom feed (file: {path})")
            return False, "ERR_NO_LNK"
        else:
            logger.info("Link tag present.")

        if root.find(f"{ATOM_NS}id") is None:
            logger.error(f"No <id> found in Atom feed (file: {path})")
            return False, "ERR_NO_IDN"
        else:
            logger.info("ID tag present.")

        if root.find(f"{ATOM_NS}updated") is None:
            logger.error(f"No <updated> found in Atom feed (file: {path})")
            return False, "ERR_NO_UPD"
        else:
            logger.info("Updated tag present.")

        # All Atom checks passed
        logger.info("All checks passed")
        return True, "INF_ALL_OK"


    # UNKNOWN FEED TYPE
    else:
        logger.error(f"Unknown feed type in validateFields: {feedType} (file: {path})")
        return False, "ERR_UNK_FEED"
