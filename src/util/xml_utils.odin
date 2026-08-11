package mrssutil

import "core:encoding/xml"
import "core:strings"


//Various utilities for dealing with XML files

// Helper: Get attribute value from an element
// Returns empty string if attribute doesn't exist
get_attrib :: proc(element: ^xml.Element, key: string) -> string {
    for attr in element.attribs {
        if attr.key == key {
            return attr.val
        }
    }
    return ""
}
// text_content recursively extracts all text from an element and its children
text_content :: proc(doc: ^xml.Document, elem: ^xml.Element) -> string {
    if elem == nil || doc == nil {
        return ""
    }

    builder := strings.builder_make(context.temp_allocator)

    for v in elem.value {
        switch v in v {
            case string:
                strings.write_string(&builder, v)
            case xml.Element_ID:
                child := &doc.elements[v]
                strings.write_string(&builder, text_content(doc, child))
        }
    }

    return strings.to_string(builder)
}

// get_text extracts text content from a child element
get_text :: proc(doc: ^xml.Document, parent_id: u32, tag: string) -> string {
    child_id, found := xml.find_child_by_ident(doc, parent_id, tag, 0)
    if !found {
        return ""
    }
    child := &doc.elements[child_id]
    return text_content(doc, child)
}

// get_text_from_element extracts text content from an element directly
get_text_from_element :: proc(doc: ^xml.Document, element_id: u32) -> string {
    if element_id == 0 {
        return ""
    }
    elem := &doc.elements[element_id]
    return text_content(doc, elem)
}

// get_all_children gets all children of a specific type
get_all_children :: proc(doc: ^xml.Document, parent_id: u32, tag: string) -> []u32 {
    children: [dynamic]u32
    i := 0
    for {
        child_id, found := xml.find_child_by_ident(doc, parent_id, tag, i)
        if !found { break }
        append(&children, child_id)
        i += 1
    }
    return children[:]
}
