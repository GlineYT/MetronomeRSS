package mrssui


import "core:fmt"
import "core:log"
import "vendor:microui"
import parser "../parser"

main :: proc() {
  //create a logger
	context.logger = log.create_console_logger()
	path := "/home/kingmarkoxiv/Desktop/UKTC/other_files/randomcode/odin/Metronome RSS/test/sample-rss-091.xml"
	log.debug("Metronome RSS started")
	log.info("Attempting to load example RSS feed with path ", path)
	doc, error := parser.loadfeed(path)
	type,valid := parser.validatefeed(doc,path)
	log.infof("Example RSS feed loaded: type=%s, valid=%v", type, valid)
	log.infof("Attempting to parse, path")
}
