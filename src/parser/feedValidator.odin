package mrssparser

import "core:fmt"
import "core:log"
import "core:encoding/xml"

import util "../util"


// RSS format validator
// Pointer to xml document and filepath to file
validatefeed :: proc(doc: ^xml.Document, path: string) -> (feedType: string, valid: bool, error: string) {
    feedType = "Unknown"
    valid = false
    error = "ERR_UNK_FEED"

    root := &doc.elements[0]
    if root == nil {
        log.errorf("Invalid RSS format: no root element in file %s", path)
        error = "ERR_NO_RSS"
        return feedType, valid, error
    }

    // RSS 1.0 (RDF)
    if root.ident == "RDF" || root.ident == "rdf:RDF" {
        rss_ns := util.get_attrib(root, "xmlns")
        if rss_ns == "http://purl.org/rss/1.0/" {
            log.infof("Valid RSS 1.0 (RDF) from file: %s", path)
            feedType = "RSS_1_0"
            valid = true
            error = "INF_ALL_OK"
            return feedType, valid, error
        }
    }

    // Standard RSS versions
    if root.ident == "rss" {
        version := util.get_attrib(root, "version")

        switch version {
            case "0.90":
                log.infof("Valid RSS 0.90 from file: %s", path)
                feedType = "RSS_0_90"
                valid = true
                error = "INF_ALL_OK"
                return feedType, valid, error

            case "0.91":
                log.infof("Valid RSS 0.91 from file: %s", path)
                feedType = "RSS_0_91"
                valid = true
                error = "INF_ALL_OK"
                return feedType, valid, error

            case "0.92":
                log.infof("Valid RSS 0.92 from file: %s", path)
                feedType = "RSS_0_92"
                valid = true
                error = "INF_ALL_OK"
                return feedType, valid, error

            case "1.0":
                log.infof("Valid RSS 1.0 from file: %s", path)
                feedType = "RSS_1_0"
                valid = true
                error = "INF_ALL_OK"
                return feedType, valid, error

            case "2.0":
                log.infof("Valid RSS 2.0 from file: %s", path)
                feedType = "RSS_2_0"
                valid = true
                error = "INF_ALL_OK"
                return feedType, valid, error

            case:
                log.warnf("Unknown RSS version '%s' in file: %s", version, path)
                feedType = "Unknown"
                valid = false
                error = "ERR_UNK_RSS"
                return feedType, valid, error
        }
    }

    // Atom feeds
    if root.ident == "feed" {
        xmlns := util.get_attrib(root, "xmlns")

        switch xmlns {
            case "http://www.w3.org/2005/Atom":
                log.infof("Valid Atom 1.0 from file: %s", path)
                feedType = "Atom_1_0"
                valid = true
                error = "INF_ALL_OK"
                return feedType, valid, error

            case "http://purl.org/atom/ns#":
                log.infof("Valid Atom 0.3 from file: %s", path)
                feedType = "Atom_0_3"
                valid = true
                error = "INF_ALL_OK"
                return feedType, valid, error

            case:
                version := util.get_attrib(root, "version")
                if version == "0.3" {
                    log.infof("Valid Atom 0.3 from file: %s", path)
                    feedType = "Atom_0_3"
                    valid = true
                    error = "INF_ALL_OK"
                    return feedType, valid, error
                }
                log.warnf("Unknown Atom feed (xmlns: %s) in file: %s", xmlns, path)
                feedType = "Unknown"
                valid = false
                error = "ERR_UNK_ATM"
                return feedType, valid, error
        }
    }

    log.errorf("Unknown feed format (root: %s) in file: %s", root.ident, path)
    feedType = "Unknown"
    valid = false
    error = "ERR_UNK_FEED"
    return feedType, valid, error
}

//Check for required fields by fields. Returns wether it's valid and a error string
checkFields :: proc(doc: ^xml.Document, path: string, feedType: string) -> (valid: bool, error: string) {
    root_id: u32 = 0  // Root is always the first element

    // RSS FEEDS

    if feedType == "RSS_0_90" || feedType == "RSS_0_91" || feedType == "RSS_0_92" ||
        feedType == "RSS_1_0" || feedType == "RSS_2_0" {

            log.infof("Checking for channel in RSS feed from file: %s", path)

            // Check for channel
            channel_id, found := xml.find_child_by_ident(doc, root_id, "channel", 0)
            if !found {
                log.errorf("No channel found in file: %s", path)
                valid = false
                error = "ERR_NO_CNL"
                return valid, error
            }else {
                log.infof("Channel tag present.")
            }

            // Check for title
            _, found = xml.find_child_by_ident(doc, channel_id, "title", 0)
            if !found {
                log.errorf("No <title> found in channel (file: %s)", path)
                valid = false
                error = "ERR_NO_TTL"
                return valid, error
            }else {
                log.infof("Title tag present.")
            }

            // Check for description
            _, found = xml.find_child_by_ident(doc, channel_id, "description", 0)
            if !found {
                log.errorf("No <description> found in channel (file: %s)", path)
                valid = false
                error = "ERR_NO_DSC"
                return valid, error
            }else {
                log.infof("Description tag present.")
            }

            // Check for link
            _, found = xml.find_child_by_ident(doc, channel_id, "link", 0)
            if !found {
                log.errorf("No <link> found in channel (file: %s)", path)
                valid = false
                error = "ERR_NO_LNK"
                return valid, error
            } else {
                log.infof("Link tag present.")
            }

            // RSS 0.91 requires language
            if feedType == "RSS_0_91" {
                log.infof("RSS 0.91 feed detected, checking for <language>")
                _, found = xml.find_child_by_ident(doc, channel_id, "language", 0)
                if !found {
                    log.warnf("RSS 0.91 feed missing <language> (file: %s)", path)
                    error = "WRN_NO_LNG"  // Warning only
                    // Don't return - let it continue
                } else {
                    log.infof("Language tag present.")
                }
            }

            // RSS 1.0 requires RDF namespace
            if feedType == "RSS_1_0" {
                log.infof("RSS 1.0 feed detected, checking for RDF namespace")
                root_elem := &doc.elements[root_id]
                rdf_ns := util.get_attrib(root_elem, "xmlns:rdf")
                if rdf_ns != "http://www.w3.org/1999/02/22-rdf-syntax-ns#" {
                    log.errorf("RSS 1.0 feed missing or incorrect RDF namespace (file: %s)", path)
                    valid = false
                    error = "ERR_NO_RDF"
                    return valid, error
                }
                log.infof("RDF namespace present.")
            }

            // All RSS checks passed
            valid = true
            if error == "" {
                error = "INF_ALL_OK"
            }
            return valid, error
        }


        // ATOM FEEDS

        if feedType == "Atom_0_3" || feedType == "Atom_1_0" {
            log.infof("Checking Atom feed: %s", path)

            // Atom requires: title, link, id, updated
            _, found := xml.find_child_by_ident(doc, root_id, "title", 0)
            if !found {
                log.errorf("No <title> found in Atom feed (file: %s)", path)
                valid = false
                error = "ERR_NO_TTL"
                return valid, error
            } else {
                log.infof("Title tag present.")
            }

            _, found = xml.find_child_by_ident(doc, root_id, "link", 0)
            if !found {
                log.errorf("No <link> found in Atom feed (file: %s)", path)
                valid = false
                error = "ERR_NO_LNK"
                return valid, error
            } else {
                log.infof("Language tag present.")
            }

            _, found = xml.find_child_by_ident(doc, root_id, "id", 0)
            if !found {
                log.errorf("No <id> found in Atom feed (file: %s)", path)
                valid = false
                error = "ERR_NO_IDN"
                return valid, error
            } else {
                log.infof("ID tag present.")
            }

            _, found = xml.find_child_by_ident(doc, root_id, "updated", 0)
            if !found {
                log.errorf("No <updated> found in Atom feed (file: %s)", path)
                valid = false
                error = "ERR_NO_UPD"
                return valid, error
            } else {
                log.infof("Updated tag present.")
            }

            // All Atom checks passed
            valid = true
            error = "INF_ALL_OK"
            return valid, error
        }

        // UNKNOWN FEED TYPE

        log.errorf("Unknown feed type in checkFields: %s (file: %s)", feedType, path)
        valid = false
        error = "ERR_UNK_FEED"
        return valid, error
}
