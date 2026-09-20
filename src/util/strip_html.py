import re

def _strip_html(text):
    """Remove HTML tags and decode common entities so descriptions read cleanly."""
    if not text:
        return ""
    text = re.sub(r"<[^>]+>", " ", text)
    text = (text
            .replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
            .replace("&quot;", '"').replace("&#39;", "'").replace("&nbsp;", " "))
    return " ".join(text.split()).strip()
