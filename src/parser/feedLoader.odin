package mrssparser

import "core:fmt"
import "core:log"	
import "core:encoding/xml"
import "core:os"

//XML loading function. Will load the XML file and validate for errors. Returns a pointer to the document and a error.
//The string is a filepath
loadfeed ::  proc(path: string) -> (^xml.Document, xml.Error) {
  //create a logger
  context.logger = log.create_console_logger()
  log.infof("Loader called with filepath: %s", path)


  //Document loading
  doc, err := xml.load_from_file(path)
    if err != nil { 
        log.errorf("error loading file",path,"with error",err)
        return nil, err
    }
    
    //pass ownership to caller
    return doc, nil
	

}
