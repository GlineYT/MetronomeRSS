import logging
import sys
import pygame

from pathlib import Path

from src.ui.components import button
from src.ui.components import sidebar
from src.ui.components import item_tile
from src.ui.components import modal
from src.ui.components import text_input
from src.ui.components import checkbox
from src.ui.components import topbar

from src.parser import pipeline

from src.util import strip_html

from src.net import downloader

from src.user import config_crud

logger = logging.getLogger(__name__)


# --- Grid layout constants ---
TILE_SIZE = 300
TILE_GAP = 10
COLS = 6
CONTENT_TOP = 60  # Below the navbar

# --- Modal layout constants ---
MODAL_WIDTH = 700
MODAL_HEIGHT = 600
MODAL_PADDING = 20



def _parse_feed(path):
    logger.info("Initializing pipeline")
    return pipeline.init_pipeline(path)


def _extract_items(parsed_feed):
    """Extract (title, description, metadata_dict) tuples from a parsed feed."""
    items = []
    if not parsed_feed:
        return items

    if parsed_feed.get("feed_type") == "RSS" and "rss" in parsed_feed:
        channel = parsed_feed["rss"]
        channel_title = channel.get("title", "Unknown source")
        for item in channel.get("items", []):
            title = item.get("title", "Untitled")
            description = strip_html._strip_html(item.get("description", ""))
            pub_date = item.get("pub_date", "")

            # Split pub_date into date and time if it looks like an RFC822 string
            date_str = pub_date
            time_str = ""
            if pub_date and " " in pub_date:
                parts = pub_date.split(" ")
                if len(parts) >= 5:
                    # "Tue, 26 Oct 2004 14:01:01 -0500" -> date: "26 Oct 2004", time: "14:01"
                    date_str = f"{parts[1]} {parts[2]} {parts[3]}"
                    time_str = parts[4][:5]  # "14:01"

            metadata = {
                "source": channel_title,
                "link": item.get("link", ""),
                "time": time_str,
                "date": date_str,
            }
            items.append((title, description, metadata))
    return items

def _load_feeds(state):
    """Load and parse all saved feeds from the current profile."""
    profile_path = state.get("selected_profile_path")
    if not profile_path:
        logger.warning("No profile path — cannot load feeds")
        state["feed_items"] = []
        state["feed_title"] = "(no profile)"
        return

    # --- Get saved feed URLs from the profile ---
    feeds = config_crud.update_user_data(profile_path, "feeds", "read")
    if not feeds:
        logger.info("No saved feeds — starting with empty list")
        state["feed_items"] = []
        state["feed_title"] = "All RSS feeds"
        return

    tmp_dir = Path(state["profile_directory"]) / "tmp"
    all_items = []

    for feed_entry in feeds:
        url = feed_entry.get("link") if isinstance(feed_entry, dict) else feed_entry
        if not url:
            continue

        logger.info(f"Loading feed: {url}")

        # --- Download ---
        paths, error = downloader.downloadRSS([url], destination=tmp_dir)
        if error != downloader.INF_DL_ALL_OK or not paths:
            logger.error(f"Failed to download {url}: {error}")
            continue

        # --- Parse ---
        parsed = pipeline.init_pipeline(paths[0])
        if parsed is None:
            logger.error(f"Failed to parse {paths[0]}")
            continue

        # --- Extract items ---
        all_items.extend(_extract_items(parsed))

    state["feed_items"] = all_items
    state["feed_title"] = f"All RSS feeds ({len(feeds)} feeds)"
    logger.info(f"Loaded {len(all_items)} items from {len(feeds)} feeds")

def _setup_item_layout(state, content_x, content_y):
    layout = []
    for i, (title, description, metadata) in enumerate(state["feed_items"]):
        col = i % COLS
        row = i // COLS
        x = content_x + col * (TILE_SIZE + TILE_GAP)
        y = content_y + row * (TILE_SIZE + TILE_GAP)
        layout.append([x, y, TILE_SIZE, TILE_SIZE, title, description, metadata])
    state["feed_item_layout"] = layout

def init(state):
    logger.info(f"Initializing feed screen for {state['selected_profile']}")
    state["feed_scroll"] = 0
    state["sidebar_open"] = False
    state["selected_section"] = "All RSS feeds"

    # Feed data
    state["feed_items"] = []
    state["feed_title"] = ""
    state["feed_item_layout"] = []

    # Modal state
    state["show_modal"] = False
    state["modal_title"] = ""
    state["modal_description"] = ""
    state["modal_rect"] = None
    state["modal_metadata"] = {}
    state["modal_title_scroll"] = 0

    # Net I/O state
    state["downloading_feed"] = False
    state["download_text_buffer"] = [""]
    state["download_error"] = None

    # Screen state
    state["block_background_input"] = False
    state["block_hover"] = False
    #Checkbox states
    state["checkbox_add_to_feedlist"] = False

    _load_feeds(state)

def _draw_download_overlay(state, mouse_pos, clicked, events):
    """Draws the download URL input overlay."""
    screen = state["screen"]
    font = state["font"]
    button_font = state["button_font"]
    state["block_background_input"] = True
    state["block_hover"] = True

    # --- Dim the background ---
    dim = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    dim.fill((0, 0, 0, 150))
    screen.blit(dim, (0, 0))

    # --- Prompt ---
    prompt_surf = button_font.render(
        "Enter the URL of the RSS feed to download:", True, (255, 255, 255)
    )
    prompt_rect = prompt_surf.get_rect(center=(screen.get_width() // 2, 400))
    screen.blit(prompt_surf, prompt_rect)

    # --- Checkbox ---
    feed_add_checkbox = checkbox.draw_checkbox(
        screen,
        screen.get_width() // 2 - 320,525,
        "Save to feeds?",state,"checkbox_add_to_feedlist",
        font,mouse_pos,clicked)


    # --- Text input ---
    result = text_input.draw_text_input(
        screen,
        screen.get_width() // 2 - 320, 450, 640,
        font, mouse_pos, clicked, events,
        state["download_text_buffer"],
        placeholder="https://example.com/feed.xml",
    )

    # --- Error message ---
    if state.get("download_error"):
        error_surf = font.render(state["download_error"], True, (255, 100, 100))
        error_rect = error_surf.get_rect(center=(screen.get_width() // 2, 520))
        screen.blit(error_surf, error_rect)

    # --- Handle submission ---
    if result is not None and result.strip() != "":
        url = result.strip()
        _perform_download(state, url)
        state["block_background_input"] = False
        state["block_hover"] = False
        if state["checkbox_add_to_feedlist"]:
            logger.info(f"Saving url {url} to user's rss feed list")
            config_crud.add_feed_to_profile(state["selected_profile_path"], url)
            state["checkbox_add_to_feedlist"] = False


    # --- Handle cancel (Escape key) ---
    for event in events:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            # --- Reset state ---
            state["downloading_feed"] = False
            state["download_error"] = None
            state["download_text_buffer"][0] = ""
            state["block_background_input"] = False
            state["block_hover"] = False
            state["checkbox_add_to_feedlist"] = False
            return

def _perform_download(state, url):
    logger.info(f"Downloading feed: {url}")
    tmp_dir = Path(state["profile_directory"]) / "tmp"
    paths, error_code = downloader.downloadRSS([url], destination=tmp_dir)

    if error_code != downloader.INF_DL_ALL_OK or not paths:
        logger.error(f"Download failed: {error_code}")
        state["download_error"] = f"Download failed: {error_code}"
        state["download_text_buffer"][0] = ""
        return

    logger.info(f"Downloaded: {paths[0]}")

    # --- Optionally save to profile ---
    if state["checkbox_add_to_feedlist"]:
        profile_path = state.get("selected_profile_path")
        if profile_path:
            logger.info(f"Saving url to profile: {url}")
            config_crud.add_feed_to_profile(profile_path, url)
            state["checkbox_add_to_feedlist"] = False
        else:
            logger.error("No profile path — cannot save feed")

    # --- Refresh the feed list ---
    state["download_error"] = None
    state["downloading_feed"] = False
    state["download_text_buffer"][0] = ""
    _load_feeds(state)

def draw(state, mouse_pos, clicked, events):
    screen = state["screen"]
    title_font = pygame.font.SysFont(None, 48)
    button_font = state["button_font"]
    small_font = state["font"]
    accent = state.get("accent_color", state["button_color"])
    profile_name = state["selected_profile"]
    section = state.get("selected_section", "All RSS feeds")

    # MODAL
    if state["show_modal"]:
        topbar.draw_topbar(
            screen, accent,
            f"{profile_name} — {section}",
            title_font, button_font,
            mouse_pos, clicked,
        )
        is_closed, modal_rect = modal.draw_modal(
            screen,
            state["modal_title"],
            state["modal_description"],
            state["modal_metadata"],
            mouse_pos,
            clicked,
            accent,
        )
        state["modal_rect"] = modal_rect
        if is_closed:
            state["show_modal"] = False
            state["modal_rect"] = None
        return

    #DOWNLOAD OVERLAY
    if state["downloading_feed"]:
        topbar.draw_topbar(
            screen, accent,
            f"{profile_name} — Download/Add RSS Feed",
            title_font, button_font,
            mouse_pos, clicked,
        )
        _draw_download_overlay(state, mouse_pos, clicked, events)
        return


    #NORMAL MODE

    bar = topbar.draw_topbar(
        screen, accent,
        f"{profile_name} — {section}",
        title_font, button_font,
        mouse_pos, clicked,
        show_hamburger=True,
        show_back=True,
        action_buttons=[
            ("Download", "download"),
            ("Reload", "reload"),
        ],
    )

    # --- HANDLE TOPBAR INTERACTIONS ---
    # The "block_background_input" flag means an overlay (like the sidebar) is
    # temporarily capturing input, so topbar clicks should be ignored.
    input_locked = state["sidebar_open"] or state["block_background_input"]

    if bar["hamburger"] and not input_locked:
        state["sidebar_open"] = not state["sidebar_open"]

    if bar["back"] and not input_locked:
        logger.info("Returning to PROFILE_SELECT")
        state["current_screen"] = "PROFILE_SELECT"
        state["selected_profile"] = None
        from src.ui.screens import profile_select
        profile_select.init(state)
        return

    if bar["actions"].get("download") and not input_locked:
        state["downloading_feed"] = True
        state["download_text_buffer"][0] = ""

    if bar["actions"].get("reload") and not input_locked:
        _load_feeds(state)

    # CONTENT AREA (Item tiles)

    content_x = int(screen.get_width() * sidebar.SIDEBAR_WIDTH_RATIO) if state["sidebar_open"] else 20
    content_y = CONTENT_TOP + 10

    layout_stale = (
        not state["feed_item_layout"]
        or len(state["feed_item_layout"]) != len(state["feed_items"])
    )
    if layout_stale:
        _setup_item_layout(state, content_x, content_y)

    # "Effective" input: suppress tile hover/clicks when the sidebar is open
    if state["sidebar_open"] or state["block_hover"]:
        effective_mouse = (-1, -1)
        effective_clicked = False
    else:
        effective_mouse = mouse_pos
        effective_clicked = clicked

    clicked_item = None
    for tile_data in state["feed_item_layout"]:
        x, y, w, h, item_title, item_desc, item_meta = tile_data
        if y > screen.get_height():
            continue
        if item_tile.draw_item_tile(
            screen, x, y, item_title, item_desc,
            effective_mouse, effective_clicked, accent, size=TILE_SIZE
        ):
            clicked_item = (item_title, item_desc, item_meta)

    if clicked_item and not state["block_background_input"]:
        state["show_modal"] = True
        state["modal_title"] = clicked_item[0]
        state["modal_description"] = clicked_item[1]
        state["modal_metadata"] = clicked_item[2]
        state["modal_title_scroll"] = 0
        clicked = False

    # SIDEBAR (drawn last, on top of everything, with its own dim)

    if not state["block_background_input"]:
        sidebar_result = sidebar.draw_sidebar(
            screen, button_font, small_font,
            mouse_pos, clicked, state["sidebar_open"], accent,
        )

        if sidebar_result == "CLOSE":
            state["sidebar_open"] = False
            _setup_item_layout(state, 20, CONTENT_TOP + 10)
        elif sidebar_result == "Quit":
            sys.exit(0)
        elif sidebar_result:
            logger.info(f"Sidebar item clicked: {sidebar_result}")
            state["selected_section"] = sidebar_result
