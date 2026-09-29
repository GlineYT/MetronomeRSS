import logging
import sys
import pygame

from pathlib import Path

from src.ui.components import button
from src.ui.components import sidebar
from src.ui.components import item_tile
from src.ui.components import modal
from src.ui.components import text_input

from src.parser import pipeline

from src.util import strip_html

from src.net import downloader

logger = logging.getLogger(__name__)


# --- Grid layout constants ---
TILE_SIZE = 300
TILE_GAP = 10
COLS = 6
CONTENT_TOP = 60  # Below the navbar




def _parse_feed(path):
    logger.info("Initializing pipeline")
    return pipeline.init_pipeline(path)


def _extract_items(parsed_feed):
    """Extract (title, description) tuples from a parsed feed dict."""
    items = []
    if not parsed_feed:
        return items

    if parsed_feed.get("feed_type") == "RSS" and "rss" in parsed_feed:
        channel = parsed_feed["rss"]
        for item in channel.get("items", []):
            title = item.get("title", "Untitled")
            description = strip_html._strip_html(item.get("description", ""))
            items.append((title, description))
    # Atom parsing goes here later.

    return items


def _load_feeds(state):
    """Parse feeds for the current profile and store items in state."""
    path = state.get("current_feed_location", "")

    if not path:
        logger.info("No feed loaded yet — starting with empty item list")
        state["feed_items"] = []
        state["feed_title"] = ""
        return

    if not Path(path).exists():
        logger.warning(f"Feed path does not exist: {path}")
        state["feed_items"] = []
        state["feed_title"] = ""
        return

    parsed = _parse_feed(path)
    state["feed_items"] = _extract_items(parsed)
    if parsed and "rss" in parsed:
        state["feed_title"] = parsed["rss"].get("title", "")
    logger.info(f"Loaded {len(state['feed_items'])} items from {path}")

def _setup_item_layout(state, content_x, content_y):
    """Compute absolute positions of all item tiles."""
    layout = []
    for i, (title, description) in enumerate(state["feed_items"]):
        col = i % COLS
        row = i // COLS
        x = content_x + col * (TILE_SIZE + TILE_GAP)
        y = content_y + row * (TILE_SIZE + TILE_GAP)
        layout.append([x, y, TILE_SIZE, TILE_SIZE, title, description])
    state["feed_item_layout"] = layout


def init(state):
    logger.info(f"Initializing feed screen for {state['selected_profile']}")
    state["feed_scroll"] = 0
    state["sidebar_open"] = False
    state["selected_section"] = "All RSS feeds"

    # Feed data
    state["current_feed_location"] = ""
    state["feed_items"] = []
    state["feed_title"] = ""
    state["feed_item_layout"] = []

    # Modal state
    state["show_modal"] = False
    state["modal_title"] = ""
    state["modal_description"] = ""
    state["modal_rect"] = None

    #netio state
    state["downloading_feed"] =  False
    state["download_text_buffer"] = [""]
    state["download_error"] = None

    # Load feeds immediately
    _load_feeds(state)

    #Screen State
    state["block_background_input"] = False
    state["block_hover"] = False

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

    # --- Handle cancel (Escape key) ---
    for event in events:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            state["downloading_feed"] = False
            state["download_error"] = None
            state["download_text_buffer"][0] = ""
            state["block_background_input"] = False
            state["block_hover"] = False
            return

def _perform_download(state, url):
    """Download a feed from a URL and refresh the feed list."""
    logger.info(f"Downloading feed: {url}")

    # Where to put it: profile_directory/tmp/
    tmp_dir = Path(state["profile_directory"]) / "tmp"

    paths, error_code = downloader.downloadRSS([url], destination=tmp_dir)

    if error_code == downloader.INF_DL_ALL_OK and paths:
        logger.info(f"Downloaded {len(paths)} file(s): {paths}")
        state["download_error"] = None
        state["downloading_feed"] = False
        state["download_text_buffer"][0] = ""
        state["current_feed_location"] = paths[0]

        # Refresh the feed list
        _load_feeds(state)
    else:
        logger.error(f"Download failed: {error_code}")
        state["download_error"] = f"Download failed: {error_code}"
        state["download_text_buffer"][0] = ""

def draw(state, mouse_pos, clicked, events):
    screen = state["screen"]
    title_font = pygame.font.SysFont(None, 48)
    button_font = state["button_font"]
    small_font = state["font"]
    accent = state.get("accent_color", state["button_color"])
    profile_name = state["selected_profile"]

    # --- MODAL GATE (if a modal is open, its input is the ONLY input) ---
    if state["show_modal"]:
        is_closed, modal_rect = modal.draw_modal(
            screen, state["modal_title"], state["modal_description"],
            mouse_pos, clicked, accent
        )
        state["modal_rect"] = modal_rect
        if is_closed:
            state["show_modal"] = False
            state["modal_rect"] = None
        return  # Don't draw anything else this frame — modal is on top

    # --- TOP BAR ---
    navbar = pygame.Rect(0, 0, screen.get_width(), 50)
    pygame.draw.rect(screen, accent, navbar)

    # --- HAMBURGER TOGGLE ---
    toggle_rect = pygame.Rect(10, 10, 30, 30)
    if toggle_rect.collidepoint(mouse_pos):
        pygame.draw.rect(screen, (255, 255, 255), toggle_rect, 2)
    for j in range(3):
        pygame.draw.rect(screen, (255, 255, 255), (14, 15 + j * 8, 22, 3))
    if toggle_rect.collidepoint(mouse_pos) and clicked:
        state["sidebar_open"] = not state["sidebar_open"]

     # --- DOWNLOAD BUTTON (next to Reload) ---
    download_button = button.draw_button(
        screen, screen.get_width() - 230, 5, "Download", button_font,
        mouse_pos, clicked, accent_color=accent
    )
    if download_button and not state["sidebar_open"] and not state["block_background_input"]:
        state["downloading_feed"] = True
        state["download_text_buffer"][0] = ""

    # --- RELOAD BUTTON ---
    reload_button = button.draw_button(
        screen, screen.get_width() - 100, 5, "Reload", button_font,
        mouse_pos, clicked, accent_color=accent
    )
    if reload_button and not state["sidebar_open"] and not state["block_background_input"]:
        _load_feeds(state)

    # --- BACK BUTTON ---
    back_button = button.draw_button(
        screen, 55, 5, "Back", button_font, mouse_pos, clicked, accent
    )
    if back_button and not state["sidebar_open"] and not state["block_background_input"]:
        logger.info("Returning to PROFILE_SELECT")
        state["current_screen"] = "PROFILE_SELECT"
        state["selected_profile"] = None
        from src.ui.screens import profile_select
        profile_select.init(state)
        return

    # --- TITLE ---
    section = state.get("selected_section", "All RSS feeds")
    title_surf = title_font.render(f"{profile_name} — {section}", True, (255, 255, 255))
    title_rect = title_surf.get_rect(center=(screen.get_width() // 2, 25))
    screen.blit(title_surf, title_rect)

    # --- CONTENT AREA (Item tiles) ---
    content_x = int(screen.get_width() * sidebar.SIDEBAR_WIDTH_RATIO) if state["sidebar_open"] else 20
    content_y = CONTENT_TOP + 10

    # Recompute layout when the sidebar opens/closes or item count changes
    layout_stale = (
        not state["feed_item_layout"]
        or len(state["feed_item_layout"]) != len(state["feed_items"])
    )
    if layout_stale:
        _setup_item_layout(state, content_x, content_y)

    # "Effective" input: when the sidebar is open, item tiles shouldn't respond
    # to hover or clicks (they're behind the dim overlay).
    if state["sidebar_open"] or state["block_hover"]:
        effective_mouse = (-1, -1)
        effective_clicked = False
    else:
        effective_mouse = mouse_pos
        effective_clicked = clicked

    # Draw tiles + handle clicks
    clicked_item = None
    for tile_data in state["feed_item_layout"]:
        x, y, w, h, item_title, item_desc = tile_data

        # Simple culling: skip tiles fully below the visible area
        if y > screen.get_height():
            continue

        if item_tile.draw_item_tile(
            screen, x, y, item_title, item_desc,
            effective_mouse, effective_clicked, accent, size=TILE_SIZE
        ):
            clicked_item = (item_title, item_desc)

    # If the download overlay is open, it owns input for this frame
    if state["downloading_feed"]:
        _draw_download_overlay(state, mouse_pos, clicked, events)
        return

    # Open modal on click
    if clicked_item and not state["block_background_input"]:
        state["show_modal"] = True
        state["modal_title"] = clicked_item[0]
        state["modal_description"] = clicked_item[1]
        clicked = False  # eat the click so nothing else sees it

    # --- SIDEBAR (drawn last, on top of everything, with its own dim) ---
    if not state["block_background_input"]:
        sidebar_result = sidebar.draw_sidebar(
            screen, button_font, small_font,
            mouse_pos, clicked, state["sidebar_open"], accent,
        )

        if sidebar_result == "CLOSE":
            state["sidebar_open"] = False
            # Sidebar changed width — recompute layout for the wider content area
            _setup_item_layout(state, 20, CONTENT_TOP + 10)
        elif sidebar_result == "Quit":
            sys.exit(0)
        elif sidebar_result:
            logger.info(f"Sidebar item clicked: {sidebar_result}")
            state["selected_section"] = sidebar_result
