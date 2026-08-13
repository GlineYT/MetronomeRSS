package mrssui

import "core:log"
import parser "../parser"

main :: proc() {
	context.logger = log.create_console_logger()
	log.debug("Console logger created")

	path := "/home/kingmarkoxiv/Desktop/UKTC/other_files/randomcode/odin/Metronome RSS/test/sample 2.xml"

	log.infof("Metronome RSS started")

	// Call the pipeline
	feedData, success, err_code := parser.feedpipeline(path)
	if !success {
		log.errorf("Pipeline failed: %s", err_code)
		return
	}

	log.infof("Pipeline succeeded! Feed type: %s", feedData.feed_type)

	// Now you can use the feedData for UI rendering
	// render_ui(feedData)
}
