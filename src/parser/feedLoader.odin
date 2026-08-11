package mrssparser

import "core:log"
import "core:encoding/xml"
import "core:os"

// XML loading function. Will load the XML file and validate for errors.
// Returns: pointer to the document, xml.Error, and a custom error code string
loadfeed :: proc(path: string) -> (^xml.Document, xml.Error, string) {
  context.logger = log.create_console_logger()
  log.infof("Loader called with filepath: %s", path)

  // Check if the file exists
  if !os.exists(path) {
    log.errorf("File does not exist: %s", path)
    return nil, nil, "ERR_NO_FILE"
  }

  //Check filesize
  // Get file info to check size
  file_info, stat_err := os.stat(path, context.allocator)
  if stat_err != nil {
    log.errorf("Failed to stat file: %s (error: %v)", path, stat_err)
    return nil, nil, "ERR_LD_FILE"
  }

  if file_info.size == 0 {
    log.errorf("File is empty: %s", path)
    return nil, nil, "ERR_INV_XML"
  }

  // XML Loading and parsing
  doc, xml_err := xml.load_from_file(path)
  if xml_err != nil {
    // XML parsing failed - invalid XML
    log.errorf("Invalid XML in file: %s (error: %v)", path, xml_err)
    return nil, xml_err, "ERR_INV_XML"
  }

  // Root element check
  if len(doc.elements) == 0 {
    log.errorf("XML document has no elements: %s", path)
    return nil, nil, "ERR_INV_XML"
  }

  // Return and pass ownership
  log.infof("Successfully loaded file: %s", path)
  return doc, nil, "INF_ALL_OK"
}
