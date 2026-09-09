# METRONOME RSS DOCUMENTATION
## User Data Storage Specification

This document describes the structure and format of user data storage for Metronome RSS.

---

## FILE
### Naming and Location

| Property | Specification |
|----------|---------------|
| **File Name** | `profile.json` |
| **Format** | JSON (RFC 8259 compliant) |
| **Directory** | Named after the profile name (e.g., `~/MetronomeRSS/Profiles/Default/`) |

---

## DATA STRUCTURE

The profile document is organized into logical groups based on function.

---

### 1. Metadata

Stores metadata about the profile file itself.

| Field | Type | Description |
|-------|------|-------------|
| `guid` | `string` (UUID v4) | Unique identifier for this profile |
| `created_date` | `string` (ISO 8601) | Date the profile was created (YYYY-MM-DD) |
| `created_time` | `string` (ISO 8601) | Time the profile was created (HH:MM:SS) |
| `modified_date` | `string` (ISO 8601) | Date the profile was last modified |
| `modified_time` | `string` (ISO 8601) | Time the profile was last modified |

**Example:**
```json
{
    "metadata": {
        "guid": "550e8400-e29b-41d4-a716-446655440000",
        "created_date": "2024-01-15",
        "created_time": "14:30:00",
        "modified_date": "2024-01-20",
        "modified_time": "09:15:30"
    }
}
```

---

### 2. Preferences

Stores user preferences and application state.

| Field | Type | Description |
|-------|------|-------------|
| `color_theme` | `Color` | RGB color object for UI theming |
| `language` | `string` | ISO 639-1 language code (e.g., `"en"`, `"fr"`) |
| `favourites` | `[]string` (URLs) | List of favorite feed URLs |
| `read_items` | `[]string` (UUIDs) | List of item UUIDs marked as read |
| `bookmarked_items` | `[]string` (UUIDs) | List of item UUIDs marked as bookmarked |
| `user_dir` | `string` | Absolute path to the user data directory |
| `caching_enabled` | `bool` | Whether to cache feed copies locally |
| `update_interval` | `integer` | User-defined update interval |
| `categories` | `[]Category` | User-defined category objects |
| `blacklist` | `[]string` (domains) | Domains excluded from feed updates |

#### Color Object

| Field | Type | Range | Description |
|-------|------|-------|-------------|
| `r` | `integer` | 0–255 | Red channel value |
| `g` | `integer` | 0–255 | Green channel value |
| `b` | `integer` | 0–255 | Blue channel value |

**Example:**
```json
{
    "color_theme": { "r": 30, "g": 144, "b": 255 },
    "language": "en",
    "favourites": ["https://example.com/feed.xml"],
    "read_items": ["550e8400-e29b-41d4-a716-446655440001"],
    "bookmarked_items": ["550e8400-e29b-41d4-a716-446655440002"],
    "user_dir": "/home/user/MetronomeRSS/Profiles/Default",
    "caching_enabled": true,
    "categories": [],
    "blacklist": ["spam-site.com", "clickbait-news.net"]
}
```

---

### 3. Category Object

Represents a user-defined or system category for organizing feeds.

| Field | Type | Description |
|-------|------|-------------|
| `name` | `string` | Display name of the category |
| `icon` | `string` (URI/URN) | Path or URL to the category icon |
| `bind_patterns` | `[]string` | Keywords/patterns that auto-assign feeds to this category |
| `is_default` | `bool` | Whether this is a pre-included default category |

**Example:**
```json
{
    "name": "Technology",
    "icon": "https://example.com/icons/tech.png",
    "bind_patterns": ["tech", "software", "programming", "AI"],
    "is_default": false
}
```

---

### 4. Feeds

Stores subscribed feeds and their associated data.

| Field | Type | Description |
|-------|------|-------------|
| `link` | `string` (URL/URN) | Feed URL (HTTP/HTTPS) or local `file://` URN |
| `category` | `string` | Category name (user-assigned or feed-provided) |
| `language` | `string` | Feed language (user-assigned or feed-provided) |
| `items` | `[]Item` | List of feed items (see Item section) |

**Example:**
```json
{
    "feeds": [
        {
            "link": "https://example.com/feed.xml",
            "category": "Technology",
            "language": "en",
            "items": [...]
        }
    ]
}
```

---

### 5. Item Object

Represents an individual feed entry/article.

| Field | Type | Description |
|-------|------|-------------|
| `guid` | `string` (UUID) | Unique identifier (generated if feed lacks one) |
| `title` | `string` | Item headline |
| `link` | `string` (URL) | Link to the full article |
| `description` | `string` | Summary or full content (HTML) |
| `pub_date` | `string` (ISO 8601) | Publication date |
| `categories` | `[]string` | Feed-provided categories/tags |
| `is_read` | `bool` | Whether the user has read this item |
| `is_bookmarked` | `bool` | Whether the user has bookmarked this item |

**Example:**
```json
{
    "guid": "550e8400-e29b-41d4-a716-446655440003",
    "title": "Metronome RSS Released",
    "link": "https://example.com/articles/metronome-rss-released",
    "description": "A new RSS reader built with Python and Odin...",
    "pub_date": "2024-01-20T09:15:30Z",
    "categories": ["Announcement", "Technology"],
    "is_read": false,
    "is_bookmarked": true
}
```

---

## STORAGE BEHAVIOR

### Caching

| Setting | Behavior |
|---------|----------|
| **`caching_enabled: true`** | Feed XML is copied to `(user_dir)/feeds/<feed_guid>.xml` |
| **`caching_enabled: false`** | Feeds are not stored locally (fetched on demand) |

### Bookmarking

| Setting | Behavior |
|---------|----------|
| **Cache enabled** | Bookmarked items are stored in `(user_dir)/saved_items/<item_guid>.xml` |
| **Cache disabled** | Bookmarked items are copied to the saved_items folder (forced caching) |

---

## FULL PROFILE EXAMPLE

```json
{
    "metadata": {
        "guid": "550e8400-e29b-41d4-a716-446655440000",
        "created_date": "2024-01-15",
        "created_time": "14:30:00",
        "modified_date": "2024-01-20",
        "modified_time": "09:15:30"
    },
    "preferences": {
        "color_theme": { "r": 30, "g": 144, "b": 255 },
        "language": "en",
        "favourites": ["https://news.ycombinator.com/rss"],
        "read_items": [],
        "bookmarked_items": [],
        "user_dir": "/home/user/MetronomeRSS/Profiles/Default",
        "caching_enabled": true,
        "update_interval": 15,
        "categories": [
            {
                "name": "Technology",
                "icon": "https://example.com/icons/tech.png",
                "bind_patterns": ["tech", "software", "coding"],
                "is_default": false
            }
        ],
        "blacklist": ["spam-site.com"]
    },
    "feeds": [
        {
            "link": "https://news.ycombinator.com/rss",
            "category": "Technology",
            "language": "en",
            "items": [
                {
                    "guid": "550e8400-e29b-41d4-a716-446655440001",
                    "title": "Metronome RSS Released",
                    "link": "https://news.ycombinator.com/item?id=12345",
                    "description": "A new RSS reader...",
                    "pub_date": "2024-01-20T09:15:30Z",
                    "categories": ["Announcement"],
                    "is_read": false,
                    "is_bookmarked": false
                }
            ]
        }
    ]
}
```

---
