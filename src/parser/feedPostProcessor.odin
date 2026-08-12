package mrssparser

import "core:log"

import util "../util"

post_process_rss_channel :: proc(channel: ^RSSChannel) {
    log.info("Beginning post processing step")
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
