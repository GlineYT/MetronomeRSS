package mrssutil

import "core:encoding/xml"


//Various utilities for dealing with RSS feeds

//Utility to get all items
get_all_items :: proc(doc: ^xml.Document, channel_id: u32) -> []u32 {
    items: [dynamic]u32
    i := 0
    for {
        item_id, found := xml.find_child_by_ident(doc, channel_id, "item", i)
        if !found { break }
        append(&items, item_id)
        i += 1
    }
    return items[:]
}
