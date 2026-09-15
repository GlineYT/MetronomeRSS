import logging
import os
import xml.etree.ElementTree as ET

logger = logging.getLogger(__name__)


def loadXML(xmlpath):
    RSStree = None
    err_code = "INF_ALL_OK"

    # Type check
    if not isinstance(xmlpath, str):
        logger.error(f"Provided path: {xmlpath!r} is not a string")
        return None, "ERR_INV_TPE"

    # Existence check
    if not os.path.exists(xmlpath):
        logger.error(f"Provided path: {xmlpath} does not exist")
        return None, "ERR_NO_FILE"

    # Attempt loading of file
    try:
        RSStree = ET.parse(xmlpath)
    except ET.ParseError as e:
        logger.error(f"Failed to parse XML: {e}")
        return None, "ERR_LD_FILE"
    except (FileNotFoundError, PermissionError) as e:
        logger.error(f"File access error: {e}")
        return None, "ERR_NO_FILE"
    except (UnicodeDecodeError, ValueError) as e:
        logger.error(f"File encoding error: {e}")
        return None, "ERR_INV_XML"
    except OSError as e:
        logger.error(f"I/O error: {e}")
        return None, "ERR_LD_FILE"

    logger.info("successfully loaded XML")
    return RSStree, err_code
