import logging
import os
import xml.etree.ElementTree as ET

def loadXML(xmlpath):
    RSStree = None  # Initialize with default value
    err_code = "INF_ALL_OK"  # Default success code

    #Type check
    if isinstance(xmlpath,str) != True:
        logging.error("Provided path:" + xmlpath + " is not a string")
        err_code = "ERR_INV_TPE"
        return None,err_code

    #Existence check
    if os.path.exists(xmlpath) != True:
        logging.error("Provided path:" + xmlpath + " does not exist")
        err_code = "ERR_NO_FILE"
        return None,err_code

    #Attempt loading of file
    try:
        RSStree = ET.parse(xmlpath)
    except ET.ParseError as e:
        logging.error(f"Failed to parse XML: {e}")
        return None, "ERR_LD_FILE"
    except Exception as e:
        logging.error(f"Unexpected error loading XML: {e}")
        return None, "ERR_UNK_ERR"

    logging.info("successfully loaded XML")
    return RSStree, err_code


