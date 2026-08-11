package mrssparser

import "core:time"
import "base:runtime"
import util "../util"


// RSS Image (nested struct)
RSSImage :: struct {
    url:         string,  // Required
    title:       string,  // Required
    link:        string,  // Required
    description: string,  // Optional
    width:       int,     // Optional (default: 88)
    height:      int,     // Optional (default: 31)
}

// RSS Category (with optional domain)
RSSCategory :: struct {
    name:   string,
    domain: string,  // Optional, e.g., "www.dmoz.com"
}

// RSS Channel (RSS 0.90, 0.91, 0.92, 2.0 compatible)
RSSChannel :: struct {
    // === REQUIRED (all RSS versions) ===
    title:       string,
    link:        string,
    description: string,

    // === RECOMMENDED / COMMON ===
    language:        string,    // Required in RSS 0.91
    last_build_date: string, // Last modified
    pub_date:        string, // Publication date
    generator:       string,    // Software that generated the feed
    copyright:       string,    // Copyright notice
    docs:            string,    // RSS spec URL

    // === CONTACT INFO ===
    managing_editor: string,    // Editor email
    web_master:      string,    // Webmaster email

    // === CATEGORY ===
    categories: []RSSCategory,  // List of categories

    // === IMAGE ===
    image: runtime.Maybe(RSSImage),      // ✅ Fixed: Optional feed logo

    // === ITEMS ===
    items: []RSSItem,

    // === METADATA ===
    version: string,   // "0.90", "0.91", "0.92", "2.0"
    feed_type: string, // "RSS" (for identification)
}

// RSS Enclosure (for podcasts/media)
RSSEnclosure :: struct {
    url:    string,
    length: i64,    // In bytes
    type:   string, // MIME type, e.g., "audio/mpeg"
}

// RSS Item
RSSItem :: struct {
    // === REQUIRED (all RSS versions) ===
    title: string,
    link:  string,

    // === RECOMMENDED ===
    description: string,    // Summary or full content
    pub_date:    string, // Publication date

    // === OPTIONAL ===
    guid:        string,    // Unique identifier (use link as fallback)
    author:      string,    // Author email
    comments:    string,    // Comments URL
    categories:  []RSSCategory,

    // === EXTENSIONS ===
    content_encoded: string,                     // Full article content (often in CDATA)
    enclosure:       runtime.Maybe(RSSEnclosure), // ✅ Fixed: Podcasts/media

    // === METADATA ===
    source:     string,  // Syndication source
    is_read:    bool,    // Reader state (not from RSS)
    is_starred: bool,    // Reader state (not from RSS)
}
