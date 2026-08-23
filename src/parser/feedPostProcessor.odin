package mrssparser

import "core:log"

import util "../util"

post_process_rss_channel :: proc(channel: ^RSSChannel) {
    log.info("Beginning post processing step for RSS feed")
    // Process channel fields
    channel.title = util.decode_html_entities(channel.title)
    channel.link = util.decode_html_entities(channel.link)
    channel.description = util.decode_html_entities(channel.description)
    channel.language = util.decode_html_entities(channel.language)
    channel.copyright = util.decode_html_entities(channel.copyright)
    channel.managing_editor = util.decode_html_entities(channel.managing_editor)
    channel.web_master = util.decode_html_entities(channel.web_master)
    channel.generator = util.decode_html_entities(channel.generator)
    channel.docs = util.decode_html_entities(channel.docs)

    // Process image
    if img, ok := channel.image.?; ok {
        img.url = util.decode_html_entities(img.url)
        img.title = util.decode_html_entities(img.title)
        img.link = util.decode_html_entities(img.link)
        img.description = util.decode_html_entities(img.description)
        channel.image = img
    }

    // Process categories
    for &cat in channel.categories {
        cat.name = util.decode_html_entities(cat.name)
        cat.domain = util.decode_html_entities(cat.domain)
    }

    // Process items
    for &item in channel.items {
        item.title = util.decode_html_entities(item.title)
        item.link = util.decode_html_entities(item.link)
        item.description = util.decode_html_entities(item.description)
        item.guid = util.decode_html_entities(item.guid)
        item.author = util.decode_html_entities(item.author)
        item.comments = util.decode_html_entities(item.comments)
        item.content_encoded = util.decode_html_entities(item.content_encoded)

        // Process item categories
        for &cat in item.categories {
            cat.name = util.decode_html_entities(cat.name)
            cat.domain = util.decode_html_entities(cat.domain)
        }
    }
}

post_process_atom_feed :: proc(feed: ^AtomFeed) {
    log.info("Beginning Atom post processing step for ATOM feed")

    // Feed fields
    feed.title = util.decode_html_entities(feed.title)
    feed.subtitle = util.decode_html_entities(feed.subtitle)
    feed.rights = util.decode_html_entities(feed.rights)
    feed.generator = util.decode_html_entities(feed.generator)
    feed.icon = util.decode_html_entities(feed.icon)
    feed.logo = util.decode_html_entities(feed.logo)

    // Link fields (all strings)
    feed.link.href = util.decode_html_entities(feed.link.href)
    feed.link.title = util.decode_html_entities(feed.link.title)

    // Categories
    for &cat in feed.categories {
        cat.term = util.decode_html_entities(cat.term)
        cat.label = util.decode_html_entities(cat.label)
        cat.scheme = util.decode_html_entities(cat.scheme)
    }

    // Authors
    for &author in feed.author {
        author.name = util.decode_html_entities(author.name)
        author.email = util.decode_html_entities(author.email)
        author.uri = util.decode_html_entities(author.uri)
    }

    // Entries
    for &entry in feed.entries {
        entry.title = util.decode_html_entities(entry.title)
        entry.summary = util.decode_html_entities(entry.summary)
        entry.content = util.decode_html_entities(entry.content)

        // Entry link
        entry.link.href = util.decode_html_entities(entry.link.href)
        entry.link.title = util.decode_html_entities(entry.link.title)

        // Entry categories
        for &cat in entry.categories {
            cat.term = util.decode_html_entities(cat.term)
            cat.label = util.decode_html_entities(cat.label)
            cat.scheme = util.decode_html_entities(cat.scheme)
        }

        // Entry authors
        for &author in entry.author {
            author.name = util.decode_html_entities(author.name)
            author.email = util.decode_html_entities(author.email)
            author.uri = util.decode_html_entities(author.uri)
        }
    }
}
