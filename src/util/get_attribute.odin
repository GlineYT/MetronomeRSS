package mrssutil

import "core:fmt"
import "core:log"	
import "core:encoding/xml"
import "core:os"

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
