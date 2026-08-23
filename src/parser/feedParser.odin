package mrssparser

import "core:log"
import "core:encoding/xml"
import "core:strconv"
import util "../util"
import "core:encoding/uuid"
import "base:runtime"

parsefeed :: proc(doc: ^xml.Document, feedType: string) -> FeedData {
	log.infof("Parser called with feed type: %s", feedType)

	// Check if it's RSS
	if feedType == "RSS_0_90" || feedType == "RSS_0_91" || feedType == "RSS_0_92" ||
		feedType == "RSS_1_0" || feedType == "RSS_2_0" {
			log.infof("Feed is RSS type. Parsing channel.")
			channel := parse_rss_channel(doc)
			return FeedData{
				rss = channel,
				feed_type = "RSS",
			}
		}

		// Check if it's Atom
		if feedType == "Atom_0_3" || feedType == "Atom_1_0" {
			log.infof("Feed is Atom type. Parsing entries.")
			feed := parse_atom_feed(doc)
			return FeedData{
				atom = feed,
				feed_type = "Atom",
			}
		}

		// Unknown type - return empty
		log.errorf("Unknown feed type for parsing: %s", feedType)
		return FeedData{
			feed_type = "Unknown",
		}
}

parse_rss_channel :: proc(doc: ^xml.Document) -> RSSChannel {
	channel := RSSChannel{
		version = "2.0",
		feed_type = "RSS",
	}

	root := &doc.elements[0]
	channel_id, _ := xml.find_child_by_ident(doc, 0, "channel", 0)

	// Required fields
	channel.title = util.get_text(doc, channel_id, "title")
	channel.link = util.get_text(doc, channel_id, "link")
	channel.description = util.get_text(doc, channel_id, "description")

	// Optional fields
	channel.language = util.get_text(doc, channel_id, "language")
	channel.copyright = util.get_text(doc, channel_id, "copyright")
	channel.generator = util.get_text(doc, channel_id, "generator")
	channel.managing_editor = util.get_text(doc, channel_id, "managingEditor")
	channel.web_master = util.get_text(doc, channel_id, "webMaster")
	channel.docs = util.get_text(doc, channel_id, "docs")

	// Parse dates
	channel.last_build_date = util.get_text(doc, channel_id, "lastBuildDate")
	channel.pub_date = util.get_text(doc, channel_id, "pubDate")

	// Parse categories
	channel.categories = parse_rss_categories(doc, channel_id)

	// Parse image
	channel.image = parse_image(doc, channel_id)

	// Parse items
	channel.items = parse_rss_items(doc, channel_id)

	log.infof("Finished parsing channel data, struct: %v", channel)

	return channel
}

parse_image :: proc(doc: ^xml.Document, parent_id: u32) -> Maybe(RSSImage) {
	image_id, found := xml.find_child_by_ident(doc, parent_id, "image", 0)
	if !found { return nil }

	img := RSSImage{
		url = util.get_text(doc, image_id, "url"),
		title = util.get_text(doc, image_id, "title"),
		link = util.get_text(doc, image_id, "link"),
		description = util.get_text(doc, image_id, "description"),
	}

	// Parse width and height (with defaults)
	if width_str := util.get_text(doc, image_id, "width"); width_str != "" {
		img.width, _ = strconv.parse_int(width_str)
	} else {
		img.width = 88  // RSS default
	}

	if height_str := util.get_text(doc, image_id, "height"); height_str != "" {
		img.height, _ = strconv.parse_int(height_str)
	} else {
		img.height = 31  // RSS default
	}

	return img
}

parse_rss_items :: proc(doc: ^xml.Document, parent_id: u32) -> []RSSItem {
	items := make([dynamic]RSSItem)
	i := 0

	for {
		item_id, found := xml.find_child_by_ident(doc, parent_id, "item", i)
		if !found { break }

		// Parse a single item
		item := parse_single_rss_item(doc, item_id)
		append(&items, item)
		i += 1
	}

	return items[:]
}

// Parse a single RSS item
parse_single_rss_item :: proc(doc: ^xml.Document, item_id: u32) -> RSSItem {
	// Get the RSS guid if it exists
	rss_guid := util.get_text(doc, item_id, "guid")

	// If no GUID exists, generate a UUID v4
	final_guid := rss_guid
	if final_guid == "" {
		// Generate a UUID v4 (non-cryptographic, fast)
		// Context needs a random generator - we can use the default one
		context.random_generator = default_random_generator()
		generated_uuid := uuid.generate_v4()
		final_guid = uuid.to_string_allocated(generated_uuid) or_else "generated-guid-fallback"
	}

	item := RSSItem{
		title = util.get_text(doc, item_id, "title"),
		link = util.get_text(doc, item_id, "link"),
		description = util.get_text(doc, item_id, "description"),
		pub_date = util.get_text(doc, item_id, "pubDate"),
		guid = final_guid,  // Use RSS guid if present, otherwise generated
		author = util.get_text(doc, item_id, "author"),
		comments = util.get_text(doc, item_id, "comments"),
		content_encoded = util.get_text(doc, item_id, "content:encoded"),
		source = util.get_text(doc, item_id, "source"),
		categories = parse_rss_categories(doc, item_id),  // Parse item categories
		enclosure = parse_rss_enclosure(doc, item_id),
	}

	return item
}

// Parse RSS categories (works for both channel and item level)
parse_rss_categories :: proc(doc: ^xml.Document, parent_id: u32) -> []RSSCategory {
	categories := make([dynamic]RSSCategory)
	i := 0

	for {
		cat_id, found := xml.find_child_by_ident(doc, parent_id, "category", i)
		if !found { break }

		cat := RSSCategory{
			name = util.get_text_from_element(doc, cat_id),
			domain = util.get_attrib(&doc.elements[cat_id], "domain"),
		}
		append(&categories, cat)
		i += 1
	}

	return categories[:]
}
// Parse RSS enclosure (for podcasts/media)
parse_rss_enclosure :: proc(doc: ^xml.Document, parent_id: u32) -> runtime.Maybe(RSSEnclosure) {
	enclosure_id, found := xml.find_child_by_ident(doc, parent_id, "enclosure", 0)
	if !found { return nil }

	// ✅ Get the element pointer
	enclosure_elem := &doc.elements[enclosure_id]

	enc := RSSEnclosure{
		url  = util.get_attrib(enclosure_elem, "url"),
		type = util.get_attrib(enclosure_elem, "type"),
	}

	if length_str := util.get_attrib(enclosure_elem, "length"); length_str != "" {
		enc.length, _ = strconv.parse_i64(length_str)
	}

	return enc
}

// Helper to get a default random generator for UUID generation
default_random_generator :: proc() -> runtime.Random_Generator {
	// Use the default context random generator
	return context.random_generator
}


// Atom parsing
parse_atom_feed :: proc(doc: ^xml.Document) -> AtomFeed {
	log.infof("Parsing Atom feed")

	feed := AtomFeed{
		feed_type = "Atom",
	}

	root_id: u32 = 0
	root := &doc.elements[root_id]

	// Atom feed elements are direct children of the root
	feed.title = util.get_text(doc, root_id, "title")
	feed.id = util.get_text(doc, root_id, "id")
	feed.updated = util.get_text(doc, root_id, "updated")
	feed.subtitle = util.get_text(doc, root_id, "subtitle")
	feed.rights = util.get_text(doc, root_id, "rights")
	feed.generator = util.get_text(doc, root_id, "generator")
	feed.icon = util.get_text(doc, root_id, "icon")
	feed.logo = util.get_text(doc, root_id, "logo")

	// Parse authors
	feed.author = parse_atom_persons(doc, root_id, "author")

	// Parse categories
	feed.categories = parse_atom_categories(doc, root_id)

	// Parse links
	feed.link = parse_atom_link(doc, root_id)

	// Parse entries
	feed.entries = parse_atom_entries(doc, root_id)

	log.infof("Finished parsing Atom feed: %s", feed.title)
	return feed
}

// Parse Atom person elements (author, contributor)
parse_atom_persons :: proc(doc: ^xml.Document, parent_id: u32, tag: string) -> []AtomPerson {
	persons := make([dynamic]AtomPerson)
	i := 0

	for {
		person_id, found := xml.find_child_by_ident(doc, parent_id, tag, i)
		if !found { break }

		person := AtomPerson{
			name = util.get_text(doc, person_id, "name"),
			email = util.get_text(doc, person_id, "email"),
			uri = util.get_text(doc, person_id, "uri"),
		}
		append(&persons, person)
		i += 1
	}

	return persons[:]
}

// Parse Atom categories
parse_atom_categories :: proc(doc: ^xml.Document, parent_id: u32) -> []AtomCategory {
	categories := make([dynamic]AtomCategory)
	i := 0

	for {
		cat_id, found := xml.find_child_by_ident(doc, parent_id, "category", i)
		if !found { break }

		// Category attributes
		cat_elem := &doc.elements[cat_id]
		cat := AtomCategory{
			term = util.get_attrib(cat_elem, "term"),
			scheme = util.get_attrib(cat_elem, "scheme"),
			label = util.get_attrib(cat_elem, "label"),
		}
		append(&categories, cat)
		i += 1
	}

	return categories[:]
}

// Parse the main Atom link (rel="alternate")
parse_atom_link :: proc(doc: ^xml.Document, parent_id: u32) -> AtomLink {
	// Find the link with rel="alternate"
	i := 0
	for {
		link_id, found := xml.find_child_by_ident(doc, parent_id, "link", i)
		if !found { break }

		link_elem := &doc.elements[link_id]
		rel := util.get_attrib(link_elem, "rel")

		if rel == "alternate" || rel == "" {
			// This is the main link
			return AtomLink{
				href = util.get_attrib(link_elem, "href"),
				rel = rel,
				type = util.get_attrib(link_elem, "type"),
				hreflang = util.get_attrib(link_elem, "hreflang"),
				title = util.get_attrib(link_elem, "title"),
				length = parse_length_attr(util.get_attrib(link_elem, "length")),
			}
		}
		i += 1
	}

	return AtomLink{} // No alternate link found
}

// Parse Atom entries
parse_atom_entries :: proc(doc: ^xml.Document, parent_id: u32) -> []AtomEntry {
	entries := make([dynamic]AtomEntry)
	i := 0

	for {
		entry_id, found := xml.find_child_by_ident(doc, parent_id, "entry", i)
		if !found { break }

		entry := parse_single_atom_entry(doc, entry_id)
		append(&entries, entry)
		i += 1
	}

	return entries[:]
}

// Parse a single Atom entry
parse_single_atom_entry :: proc(doc: ^xml.Document, entry_id: u32) -> AtomEntry {
	entry := AtomEntry{
		title = util.get_text(doc, entry_id, "title"),
		id = util.get_text(doc, entry_id, "id"),
		updated = util.get_text(doc, entry_id, "updated"),
		published = util.get_text(doc, entry_id, "published"),
		summary = util.get_text(doc, entry_id, "summary"),
		content = util.get_text(doc, entry_id, "content"),
		is_read = false,
		is_starred = false,
	}

	// Parse link
	entry.link = parse_atom_entry_link(doc, entry_id)

	// Parse authors
	entry.author = parse_atom_persons(doc, entry_id, "author")

	// Parse categories
	entry.categories = parse_atom_categories(doc, entry_id)

	// Parse source (optional)
	source_id, found := xml.find_child_by_ident(doc, entry_id, "source", 0)
	if found {
		source := parse_atom_feed(doc) // Recursively parse source as a feed
		entry.source = source
	}

	return entry
}

// Parse link for an entry (find the alternate link)
parse_atom_entry_link :: proc(doc: ^xml.Document, parent_id: u32) -> AtomLink {
	i := 0
	for {
		link_id, found := xml.find_child_by_ident(doc, parent_id, "link", i)
		if !found { break }

		link_elem := &doc.elements[link_id]
		rel := util.get_attrib(link_elem, "rel")

		if rel == "alternate" || rel == "" {
			return AtomLink{
				href = util.get_attrib(link_elem, "href"),
				rel = rel,
				type = util.get_attrib(link_elem, "type"),
				hreflang = util.get_attrib(link_elem, "hreflang"),
				title = util.get_attrib(link_elem, "title"),
				length = parse_length_attr(util.get_attrib(link_elem, "length")),
			}
		}
		i += 1
	}

	return AtomLink{} // No alternate link found
}

// Helper: parse length attribute from string
parse_length_attr :: proc(length_str: string) -> i64 {
	if length_str == "" {
		return 0
	}
	val, _ := strconv.parse_i64(length_str)
	return val
}
