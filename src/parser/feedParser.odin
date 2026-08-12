package mrssparser

import "core:log"
import "core:encoding/xml"
import "core:strconv"
import util "../util"


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
		//if feedType == "Atom_0_3" || feedType == "Atom_1_0" {
			//log.infof("Feed is Atom type. Parsing entries.")
			// feed := parse_atom_feed(doc)
			//return FeedData{
			//	atom = feed,
			//	feed_type = "Atom",
			//}
		//}

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
	if last_build := util.get_text(doc, channel_id, "lastBuildDate"); last_build != "" {
		channel.last_build_date = util.get_text(doc, channel_id, "lastBuildDate")
	}
	if pub_date := util.get_text(doc, channel_id, "pubDate"); pub_date != "" {
		channel.pub_date = util.get_text(doc, channel_id, "pubDate")
	}

	// Parse categories
	//channel.categories = parse_categories(doc, channel_id)

	// Parse image
	channel.image = parse_image(doc, channel_id)

	// Parse items
	//channel.items = parse_rss_items(doc, channel_id)

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

//TODO: Category parsing function. Takes a document and channel_id
//Returns a struct


// TODO: Item parsing function. Takes a document and channel_id, returns a struct
