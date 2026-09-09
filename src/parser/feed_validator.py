#file that validates a feed
import logging

#Validates a RSS feed for validity.
logger = logging.getLogger(__name__)
#Namespace declaration
ATOM_NS = "{http://www.w3.org/2005/Atom}"

#Check if the root element exists, and what type of feed it is
def validateFeedType(RSStree,path):
    logger.info(" Beginning feed validation")
    #Default values
    feedType = "Unknown"
    valid = False
    error = "ERR_UNK_FEED"

    #Root of the file
    root = RSStree.getroot()
    logger.info("Root element:" + root.tag)
    print(root.tag)

    #check for RSS
    if root.tag == "rss":
        logger.info("feed is of type RSS")
        #get the version
        version = root.attrib["version"] #root.attrib is a dict, so the "version" key is to be taken
        logger.info(f"RSS Feed version is: {version}")

        if version == "0.90":
                logger.info("Valid RSS 0.90 from file: " + path)
                feedType = "RSS_0_90"
                valid = True
                error = "INF_ALL_OK"
                return feedType, valid, error


        elif version == "0.91":
                logger.info("Valid RSS 0.91 from file: " + path)
                feedType = "RSS_0_91"
                valid = True
                error = "INF_ALL_OK"
                return feedType, valid, error

        elif version == "0.92":
                logger.info("Valid RSS 0.92 from file:" + path)
                feedType = "RSS_0_92"
                valid = True
                error = "INF_ALL_OK"
                return feedType, valid, error

        elif version == "2.0":
                logger.info("Valid RSS 2.0 from file:" + path)
                feedType = "RSS_2_0"
                valid = True
                error = "INF_ALL_OK"
                return feedType, valid, error

        else:
                logger.error(f"Unknown RSS version {version}  in file:  {path}")
                feedType = "Unknown"
                valid = False
                error = "ERR_UNK_RSS"
                return feedType, valid, error


    #check for Atom
    elif root.tag == "{http://www.w3.org/2005/Atom}feed":
        logger.info("feed is of type Atom")
        #get the version
        feedType = "Atom_1_0"
        valid = True
        error = "INF_ALL_OK"
        return feedType, valid, error

    #If it's neither'
    elif root.tag != "rss" or root.tag != "{http://www.w3.org/2005/Atom}feed":
        logger.error("Unknown feed type")
        return feedType,valid,error,root

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

        # RSS 0.91 requires language
        if feedType == "RSS_0_91":
            logger.info("RSS 0.91 feed detected, checking for <language>")
            if channel.find("language") is None:
                logger.warning(f"RSS 0.91 feed missing <language> (file: {path})")
                error = "WRN_NO_LNG"  # Warning only
                # Don't return - let it continue
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
