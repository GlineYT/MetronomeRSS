package mrssparser

import "core:log"
import "core:fmt"

feedpipeline :: proc(path: string) -> (feedData: FeedData, success: bool, err_code: string) {
    log.infof("Attempting to load RSS/Atom feed: %s", path)

    // Load the file
    doc, xml_err, load_code := loadfeed(path)
    if load_code != "INF_ALL_OK" {
        log.errorf("Failed to load feed: %s (code: %s)", path, load_code)
        if xml_err != nil {
            log.errorf("XML error: %v", xml_err)
        }
        return FeedData{}, false, load_code
    }
    log.infof("Feed loaded successfully: %s", load_code)

    // Detect the type
    feed_type, valid, validate_error := validatefeed(doc, path)
    if !valid {
        log.errorf("Invalid feed format: %s (error: %s)", path, validate_error)
        return FeedData{}, false, validate_error
    }
    log.infof("Detected feed type: %s", feed_type)

    // Check the fields
    fields_valid : bool
    fields_valid,err_code = checkFields(doc, path, feed_type)
    if !fields_valid {
        log.errorf("Feed validation failed: %s", err_code)
        return FeedData{}, false, err_code
    }
    log.infof("All required fields present: %s", err_code)

    log.infof("Feed loaded and validated successfully!")

    // Parse
    log.infof("Attempting parse")
    feedData = parsefeed(doc, feed_type)

    // Post-process based on feed type
    if feedData.feed_type == "RSS" {
        if rss_channel, ok := feedData.rss.?; ok {
            post_process_rss_channel(&rss_channel)
            feedData.rss = rss_channel

            // Debug pretty-print
            log.info("Pretty-printing RSS feed")
            fmt.println("=== RSS FEED ===")
            fmt.println("Title:", rss_channel.title)
            fmt.println("Description:", rss_channel.description)
            fmt.println("Items:", len(rss_channel.items))
            for item, i in rss_channel.items {
                fmt.printf("  %d. %s\n", i+1, item.title)
            }
        }
    } else if feedData.feed_type == "Atom" {
        if atom_feed, ok := feedData.atom.?; ok {
            post_process_atom_feed(&atom_feed)
            feedData.atom = atom_feed

            // Debug pretty-print
            log.info("Pretty-printing Atom feed")
            fmt.println("=== ATOM FEED ===")
            fmt.println("Title:", atom_feed.title)
            fmt.println("Subtitle:", atom_feed.subtitle)
            fmt.println("Entries:", len(atom_feed.entries))
            for entry, i in atom_feed.entries {
                fmt.printf("  %d. %s\n", i+1, entry.title)
            }
        }
    } else {
        log.errorf("Unknown feed type for post-processing: %s", feedData.feed_type)
        return FeedData{}, false, "ERR_UNK_FEED"
    }

    return feedData, true, "INF_ALL_OK"
}
