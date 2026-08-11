package mrssui

import "core:fmt"
import "core:log"
import parser "../parser"

main :: proc() {
	context.logger = log.create_console_logger()
	log.debug("Console logger created")

	path := "/home/kingmarkoxiv/Desktop/UKTC/other_files/randomcode/odin/Metronome RSS/test/sample-rss-091.xml"

	log.infof("Metronome RSS started")
	log.infof("Attempting to load example RSS feed: %s", path)

	//Load the file
	doc, xml_err, load_code := parser.loadfeed(path)
	if load_code != "INF_ALL_OK" {
		log.errorf("Failed to load feed: %s (code: %s)", path, load_code)
		if xml_err != nil {
			log.errorf("XML error: %v", xml_err)
		}
		return
	}
	log.infof("Feed loaded successfully: %s", load_code)

	// Detect the type
	feed_type, valid,validate_error := parser.validatefeed(doc, path) //Returns feed type and validity thereof, takes document pointer and path
	if !valid {
		log.errorf("Invalid feed format: %s", path)
		return
	}
	log.infof("Detected feed type: %s", feed_type)

	//Check the fields
	fields_valid, err_code := parser.checkFields(doc, path, feed_type) //Returns field validity,error code if any
	if !fields_valid {
		log.errorf("Feed validation failed: %s", err_code)
		return
	}
	log.infof("All required fields present: %s", err_code)

	// In case of sucess
	log.infof("Feed loaded and validated successfully!")

	// Begin parsing
	log.infof("Attempting parse")

}
