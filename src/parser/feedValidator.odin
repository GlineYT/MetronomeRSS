package mrssparser

import "core:fmt"
import "core:log"
import "core:encoding/xml"

import util "../util"


//RSS format validator 
//Pointer to xml document and filepath to file
validatefeed :: proc(doc: ^xml.Document,path:string) -> (feedType:string, valid:bool) {

    //Variables
    //feedType (string) is a string of the type of RSS/ATOM feed
    //valid  (bool) is a flag,signaling wether the feed is a valid XML file or not
    
    //default assignments
    feedType = "Unknown"
    valid = false
    
    //in case of no root element
    root := &doc.elements[0]
    if root == nil {
        log.errorf("Invalid RSS format: no root element in file %s", path)
        return feedType, valid
    }
    
    // Handle RSS 1.0 (RDF) - root is often "RDF" or "rdf:RDF"
    if root.ident == "RDF" || root.ident == "rdf:RDF" {
    
        // Check for RSS namespace
        rss_ns := util.get_attrib(root, "xmlns")
        
        if rss_ns == "http://purl.org/rss/1.0/" {
            log.infof("Valid RSS 1.0 (RDF) from file: %s", path)
            feedType = "RSS_1_0"
            valid = true
            return feedType, valid
        }
    }
    
    // Handle standard RSS versions
    if root.ident == "rss" {
        version := util.get_attrib(root, "version")
        
        switch version {
        
        // RSS 0.90
        case "0.90":
            log.infof("Valid RSS 0.90 from file: %s", path)
            feedType = "RSS_0_90"
            valid = true
            return feedType, valid
            
        // RSS 0.91    
        case "0.91":
            log.infof("Valid RSS 0.91 from file: %s", path)
            feedType = "RSS_0_91"
            valid = true
            return feedType, valid
            
        // RSS 0.92
        case "0.92":
            log.infof("Valid RSS 0.92 from file: %s", path)
            feedType = "RSS_0_92"
            valid = true
            return feedType, valid

        // RSS 0.90
        case "1.0":
            log.infof("Valid RSS 1.0 from file: %s", path)
            feedType = "RSS_1_0"
            valid = true
            return feedType, valid

        //RSS 2.0
        case "2.0":
            log.infof("Valid RSS 2.0 from file: %s", path)
            feedType = "RSS_2_0"
            valid = true
            return feedType, valid

        //Unknown
        case:
            log.warnf("Unknown RSS version '%s' in file: %s", version, path)
            feedType = "Unknown"
            valid = false
            return feedType, valid
        }
    }
    
    // Handle Atom feeds
    if root.ident == "feed" {
        xmlns := util.get_attrib(root, "xmlns")
        
        switch xmlns {

        //Atom 1
        case "http://www.w3.org/2005/Atom":
            log.infof("Valid Atom 1.0 from file: %s", path)
            feedType = "Atom_1_0"
            valid = true
            return feedType, valid

        //Atom 0.3
        case "http://purl.org/atom/ns#":
            log.infof("Valid Atom 0.3 from file: %s", path)
            feedType = "Atom_0_3"
            valid = true
            return feedType, valid

        case:
            // Check for version attribute
            version := util.get_attrib(root, "version")
            if version == "0.3" {
                log.infof("Valid Atom 0.3 from file: %s", path)
                feedType = "Atom_0_3"
                valid = true
                return feedType, valid
            }
            
            log.warnf("Unknown Atom feed (xmlns: %s) in file: %s", xmlns, path)
            feedType = "Unknown"
            valid = false
            return feedType, valid
        }
    }
    
    // Unknown feed format
    log.errorf("Unknown feed format (root: %s) in file: %s", root.ident, path)
    feedType = "Unknown"
    valid = false
    return feedType, valid
}
