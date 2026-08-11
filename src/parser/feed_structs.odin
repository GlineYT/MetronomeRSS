package mrssparser

import "core:time"
import "base:runtime"


// FeedData is a container that can hold either an RSS or Atom feed
FeedData :: struct {
    rss:  Maybe(RSSChannel),
    atom: Maybe(AtomFeed),
    feed_type: string,  // "RSS", "Atom", or "Unknown"
}
