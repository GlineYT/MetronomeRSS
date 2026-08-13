#+feature dynamic-literals

package mrssutil

import "core:strings"
import "core:strconv"
import "core:unicode/utf8"

// Entity map for named HTML entities
entity_map := map[string]string{
    // XML/HTML required entities
    "amp"   = "&",
    "lt"    = "<",
    "gt"    = ">",
    "quot"  = "\"",
    "apos"  = "'",
    "nbsp"  = " ",

    // Common HTML entities
    "copy"   = "©",
    "reg"    = "®",
    "trade"  = "™",
    "mdash"  = "—",
    "ndash"  = "–",
    "hellip" = "…",
    "bull"   = "•",
    "euro"   = "€",
    "pound"  = "£",
    "yen"    = "¥",
    "cent"   = "¢",
}

// Decode HTML entities in a string.
// First replaces all named entities from the map,
// then handles numeric entities (decimal and hex).
decode_html_entities :: proc(text: string) -> string {
    if text == "" {
        return text
    }

    result := text

    // Replace named entities (map iteration)
    for key, val in entity_map {
        entity := strings.concatenate([]string{"&", key, ";"})
        result,_ = strings.replace(result, entity, val, -1)
    }

    // andle numeric entities: &#123; and &#xABC;
    builder := strings.builder_make()
    i := 0
    n := len(result)

    for i < n {
        if result[i] == '&' {
            if i+1 < n && result[i+1] == '#' {
                start := i
                i += 2
                is_hex := false
                if i < n && (result[i] == 'x' || result[i] == 'X') {
                    is_hex = true
                    i += 1
                }
                num_start := i
                for i < n && ((is_hex && is_hex_digit(result[i])) || (!is_hex && is_digit(result[i]))) {
                    i += 1
                }
                if i < n && result[i] == ';' {
                    num_str := result[num_start:i]
                    i += 1
                    val: u64
                    ok: bool
                    if is_hex {
                        val, ok = strconv.parse_u64(num_str, 16)
                    } else {
                        val, ok = strconv.parse_u64(num_str, 10)
                    }
                    //Check to prevent overflows/invalid data
                    if ok && val <= 0x10FFFF { //This is the maximum unicode code point.
                        runes := []rune{cast(rune)val}
                        strings.write_string(&builder, utf8.runes_to_string(runes))
                    } else {
                        strings.write_string(&builder, result[start:i])
                    }
                    continue
                } else {
                    strings.write_byte(&builder, result[i-1])
                }
            } else {
                strings.write_byte(&builder, result[i])
                i += 1
                continue
            }
        } else {
            strings.write_byte(&builder, result[i])
            i += 1
        }
    }

    return strings.to_string(builder)
}

// Helper functions for digit checking
is_digit :: proc(c: u8) -> bool {
    return '0' <= c && c <= '9'
}

is_hex_digit :: proc(c: u8) -> bool {
    return is_digit(c) || ('a' <= c && c <= 'f') || ('A' <= c && c <= 'F')
}
