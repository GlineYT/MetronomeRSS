package mrssparser

import "core:fmt"
import "core:log"
import "core:encoding/xml"

//feed parsing function. Takes a pointer to the document and a RSS version string
parsefeed :: proc(doc: ^xml.Document,feedType:string) {
  //create a logger
	context.logger = log.create_console_logger()
	log.info("Parser called with file pointer: ",doc)
	log.info("Parser called with XML version: ",feedType)
	
	fmt.println("Hello from the parser!")
}
