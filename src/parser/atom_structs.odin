package mrssparser

import "base:runtime"


// Atom Person (author/contributor)
AtomPerson :: struct {
    name:  string, // Required
    email: string, // Optional
    uri:   string, // Optional (URL)
}

// Atom Link
AtomLink :: struct {
    href:     string, // Required
    rel:      string, // Optional (e.g., "alternate", "self")
    type:     string, // Optional (MIME type)
    hreflang: string, // Optional (language)
    title:    string, // Optional
    length:   i64,    // Optional (in bytes)
}

// Atom Category
AtomCategory :: struct {
    term:   string, // Required
    scheme: string, // Optional (taxonomy URL)
    label:  string, // Optional (human-readable label)
}

// Atom Feed
AtomFeed :: struct {
    // === REQUIRED ===
    title:   string,   // Feed name
    id:      string,   // Permanent unique identifier
    updated: string, // Last update time
    link:    AtomLink, // Must have rel="alternate"

    // === RECOMMENDED ===
    subtitle:  string,        // Short description
    author:    []AtomPerson,  // Feed authors
    icon:      string,        // Small icon URL
    logo:      string,        // Logo image URL
    rights:    string,        // Copyright/license info
    generator: string,        // Software that generated the feed

    // === OPTIONAL ===
    categories: []AtomCategory,
    entries:    []AtomEntry,

    // === METADATA ===
    feed_type: string, // "Atom"
}

// Atom Entry (equivalent to RSS item)
AtomEntry :: struct {
    // === REQUIRED ===
    title:   string,   // Entry title
    id:      string,   // Permanent unique identifier
    updated: string, // Last update time
    link:    AtomLink, // Must have rel="alternate"

    // === RECOMMENDED ===
    published: string,    // Original publication date
    summary:   string,       // Brief description
    content:   string,       // Full content (can be HTML)
    author:    []AtomPerson, // Entry authors

    // === OPTIONAL ===
    categories: []AtomCategory,
    source:     runtime.Maybe(AtomFeed), // ✅ Fixed: Syndication source

    // === READER STATE ===
    is_read:    bool,
    is_starred: bool,
}
