
# METRONOME RSS DOCUMENTATION
## Feed Structs

Metronome RSS's parser produces structs which are then used by the renderer and UI. The structs for RSS and Atom feeds and items have the following basic structure:

---

### RSSChannel (RSS 0.90, 0.91, 0.92,1.0, 2.0)

| Field | Type | Description | Required? |
|-------|------|-------------|-----------|
| `title` | `string` | Channel/feed name | **Yes** (all versions) |
| `link` | `string` | URL to the website | **Yes** (all versions) |
| `description` | `string` | Brief description of the feed | **Yes** (all versions) |
| `language` | `string` | Language code (e.g., "en-us") | RSS 0.91 requires, others optional |
| `last_build_date` | `time.Time` | Last modified date of the feed | Optional |
| `pub_date` | `time.Time` | Publication date of the feed | Optional |
| `generator` | `string` | Software that generated the feed | Optional |
| `copyright` | `string` | Copyright notice | Optional |
| `docs` | `string` | RSS spec URL | Optional |
| `managing_editor` | `string` | Editor email address | Optional |
| `web_master` | `string` | Webmaster email address | Optional |
| `categories` | `[]RSSCategory` | List of feed categories/tags | Optional |
| `image` | `maybe RSSImage` | Feed logo image | Optional |
| `items` | `[]RSSItem` | List of feed items | **Yes** (should have at least one) |
| `version` | `string` | RSS version ("0.90", "0.91", "0.92", "2.0") | Populated by parser |
| `feed_type` | `string` | Always "RSS" for identification | Populated by parser |

---

### RSSCategory

| Field | Type | Description |
|-------|------|-------------|
| `name` | `string` | Category name |
| `domain` | `string` | Optional taxonomy URL (e.g., "www.dmoz.com") |

---

### RSSImage

| Field | Type | Description | Default |
|-------|------|-------------|---------|
| `url` | `string` | Image URL | - |
| `title` | `string` | Image title/alt text | - |
| `link` | `string` | Link target when image is clicked | - |
| `description` | `string` | Image description | Optional |
| `width` | `int` | Image width in pixels | 88 |
| `height` | `int` | Image height in pixels | 31 |

---

### RSSItem

| Field | Type | Description | Required? |
|-------|------|-------------|-----------|
| `title` | `string` | Item headline | **Yes** |
| `link` | `string` | URL to the full article | **Yes** |
| `description` | `string` | Summary or full content | Recommended |
| `pub_date` | `time.Time` | Publication date | Optional |
| `guid` | `string` | Unique identifier | Optional (use link as fallback) |
| `author` | `string` | Author email or name | Optional |
| `comments` | `string` | Comments URL | Optional |
| `categories` | `[]RSSCategory` | Item categories/tags | Optional |
| `content_encoded` | `string` | Full article content (often in CDATA) | Optional |
| `enclosure` | `maybe RSSEnclosure` | Media file (podcasts, etc.) | Optional |
| `source` | `string` | Syndication source | Optional |
| `is_read` | `bool` | Reader state (not from RSS) | Set by reader |
| `is_starred` | `bool` | Reader state (not from RSS) | Set by reader |

---

### RSSEnclosure

| Field | Type | Description |
|-------|------|-------------|
| `url` | `string` | Media file URL |
| `length` | `i64` | File size in bytes |
| `type` | `string` | MIME type (e.g., "audio/mpeg") |

---

### AtomFeed (Atom 0.3, 1.0)

| Field | Type | Description | Required? |
|-------|------|-------------|-----------|
| `title` | `string` | Feed name | **Yes** |
| `id` | `string` | Permanent unique identifier | **Yes** |
| `updated` | `time.Time` | Last update time | **Yes** |
| `link` | `AtomLink` | Feed link (must have `rel="alternate"`) | **Yes** |
| `subtitle` | `string` | Short description | Recommended |
| `author` | `[]AtomPerson` | Feed authors | Recommended |
| `icon` | `string` | Small icon URL | Optional |
| `logo` | `string` | Logo image URL | Optional |
| `rights` | `string` | Copyright/license info | Optional |
| `generator` | `string` | Software that generated the feed | Optional |
| `categories` | `[]AtomCategory` | Feed categories/tags | Optional |
| `entries` | `[]AtomEntry` | List of feed entries | **Yes** (should have at least one) |
| `feed_type` | `string` | Always "Atom" for identification | Populated by parser |

---

### AtomLink

| Field | Type | Description |
|-------|------|-------------|
| `href` | `string` | Link URL (**Required**) |
| `rel` | `string` | Link relationship (e.g., "alternate", "self") |
| `type` | `string` | MIME type |
| `hreflang` | `string` | Language of the linked resource |
| `title` | `string` | Human-readable title |
| `length` | `i64` | Size in bytes (for media) |

---

### AtomPerson (Author/Contributor)

| Field | Type | Description |
|-------|------|-------------|
| `name` | `string` | Person's name (**Required**) |
| `email` | `string` | Email address |
| `uri` | `string` | URL/personal website |

---

### AtomCategory

| Field | Type | Description |
|-------|------|-------------|
| `term` | `string` | Category term (**Required**) |
| `scheme` | `string` | Taxonomy URL |
| `label` | `string` | Human-readable label |

---

### AtomEntry

| Field | Type | Description | Required? |
|-------|------|-------------|-----------|
| `title` | `string` | Entry headline | **Yes** |
| `id` | `string` | Permanent unique identifier | **Yes** |
| `updated` | `time.Time` | Last update time | **Yes** |
| `link` | `AtomLink` | Entry link (must have `rel="alternate"`) | **Yes** |
| `published` | `time.Time` | Original publication date | Recommended |
| `summary` | `string` | Brief description | Recommended |
| `content` | `string` | Full content (can be HTML) | Recommended |
| `author` | `[]AtomPerson` | Entry authors | Optional |
| `categories` | `[]AtomCategory` | Entry categories/tags | Optional |
| `source` | `maybe AtomFeed` | Syndication source | Optional |
| `is_read` | `bool` | Reader state (not from Atom) | Set by reader |
| `is_starred` | `bool` | Reader state (not from Atom) | Set by reader |

---

## Field Mapping: RSS vs Atom

| Purpose | RSS Field | Atom Field |
|---------|-----------|------------|
| Feed name | `title` | `title` |
| Description | `description` | `subtitle` |
| Website URL | `link` | `link.href` (with `rel="alternate"`) |
| Unique ID | (none at channel level) | `id` |
| Last update | `lastBuildDate` | `updated` |
| Language | `language` | `link.hreflang` |
| Copyright | `copyright` | `rights` |
| Author | `managingEditor` | `author[0].name` |
| Tags | `category` | `category` |
| Logo | `image.url` | `logo` / `icon` |

---

## Zero-Value Handling

All string fields default to `""` (empty string) when not present in the feed. Use this to check for missing fields:

```odin
if feed.title == "" {
    // Title is missing
}

if img, ok := feed.image.?; ok {
    // Image exists
}
```

---

## Full Quick Reference

### RSSChannel
`title`, `link`, `description`, `language`, `last_build_date`, `pub_date`, `generator`, `copyright`, `docs`, `managing_editor`, `web_master`, `categories`, `image`, `items`, `version`, `feed_type`

### RSSItem
`title`, `link`, `description`, `pub_date`, `guid`, `author`, `comments`, `categories`, `content_encoded`, `enclosure`, `source`, `is_read`, `is_starred`

### AtomFeed
`title`, `id`, `updated`, `link`, `subtitle`, `author`, `icon`, `logo`, `rights`, `generator`, `categories`, `entries`, `feed_type`

### AtomEntry
`title`, `id`, `updated`, `link`, `published`, `summary`, `content`, `author`, `categories`, `source`, `is_read`, `is_starred`

---

