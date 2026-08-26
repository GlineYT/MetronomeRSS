import html

def recursive_unescape(data, max_iterations=3):
    """Recursively unescape HTML entities with multiple passes."""
    if isinstance(data, str):
        return unescape_repeatedly(data, max_iterations)
    elif isinstance(data, dict):
        return {key: recursive_unescape(value, max_iterations) for key, value in data.items()}
    elif isinstance(data, list):
        return [recursive_unescape(item, max_iterations) for item in data]
    else:
        return data


def unescape_repeatedly(text, max_iterations=3):
    """Unescape HTML entities until no more changes."""
    result = text
    for _ in range(max_iterations):
        new_result = html.unescape(result)
        if new_result == result:
            break
        result = new_result
    return result


def post_process_rss_channel(channel):
    """Decode HTML entities in an RSS channel dict."""
    return recursive_unescape(channel)


def post_process_atom_feed(feed):
    """Decode HTML entities in an Atom feed dict."""
    return recursive_unescape(feed)
