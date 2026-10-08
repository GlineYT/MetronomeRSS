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

from src.ui.functions import feeds as feed_funcs
from src.ui.functions import net as net_funcs

logger = logging.getLogger(__name__)

# --- Grid layout constants ---
TILE_SIZE = 300
TILE_GAP = 10
COLS = 6
CONTENT_TOP = 60

# --- Modal layout constants ---
MODAL_WIDTH = 700
MODAL_HEIGHT = 600
MODAL_PADDING = 20


def _setup_item_layout(state, content_x, content_y):
    """Compute absolute positions of all item tiles."""
    layout = []
    for i, (title, description, metadata) in enumerate(state["feed_items"]):
        col = i % COLS
        row = i // COLS
        x = content_x + col * (TILE_SIZE + TILE_GAP)
        y = content_y + row * (TILE_SIZE + TILE_GAP)
        layout.append([x, y, TILE_SIZE, TILE_SIZE, title, description, metadata])
    state["feed_item_layout"] = layout


def _refresh_feed_items(state, force=False):
    """Reload feed items via the functions layer and update state."""
    profile_path = state.get("selected_profile_path")
    tmp_dir = Path(state["profile_directory"]) / "tmp"

    if force:
        items, count = feed_funcs.reload_feeds(profile_path, tmp_dir)
    else:
        items, count = feed_funcs.load_feeds(profile_path, tmp_dir)

    state["feed_items"] = items
    state["feed_title"] = f"All RSS feeds ({count} feeds)"


def init(state):
    logger.info(f"Initializing feed screen for {state['selected_profile']}")
    state["feed_scroll"] = 0
    state["sidebar_open"] = False
    state["selected_section"] = "All RSS feeds"

    state["feed_items"] = []
    state["feed_title"] = ""
    state["feed_item_layout"] = []

    state["show_modal"] = False
    state["modal_title"] = ""
    state["modal_description"] = ""
    state["modal_rect"] = None
    state["modal_metadata"] = {}
    state["modal_title_scroll"] = 0

    state["downloading_feed"] = False
    state["download_text_buffer"] = [""]
    state["download_error"] = None

    state["block_background_input"] = False
    state["block_hover"] = False
    state["checkbox_add_to_feedlist"] = False

    _refresh_feed_items(state, force=False)


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
    checkbox.draw_checkbox(
        screen,
        screen.get_width() // 2 - 320, 525,
        "Save to feeds?", state, "checkbox_add_to_feedlist",
        font, mouse_pos, clicked,
    )

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
        tmp_dir = Path(state["profile_directory"]) / "tmp"

        save_to = None
        if state["checkbox_add_to_feedlist"]:
            save_to = state.get("selected_profile_path")

        paths, error = net_funcs.perform_download(url, tmp_dir, save_to_profile=save_to)

        state["block_background_input"] = False
        state["block_hover"] = False
        state["checkbox_add_to_feedlist"] = False

        if error == "INF_ALL_OK":
            state["download_error"] = None
            state["downloading_feed"] = False
            state["download_text_buffer"][0] = ""
            _refresh_feed_items(state, force=False)
        else:
            state["download_error"] = f"Download failed: {error}"
            state["download_text_buffer"][0] = ""

    # --- Handle cancel (Escape key) ---
    for event in events:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            state["downloading_feed"] = False
            state["download_error"] = None
            state["download_text_buffer"][0] = ""
            state["block_background_input"] = False
            state["block_hover"] = False
            state["checkbox_add_to_feedlist"] = False
            return


def draw(state, mouse_pos, clicked, events):
    screen = state["screen"]
    title_font = pygame.font.SysFont(None, 48)
    button_font = state["button_font"]
    small_font = state["font"]
    accent = state.get("accent_color", state["button_color"])
    profile_name = state["selected_profile"]
    section = state.get("selected_section", "All RSS feeds")

    # --- MODAL ---
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

    # --- DOWNLOAD OVERLAY ---
    if state["downloading_feed"]:
        topbar.draw_topbar(
            screen, accent,
            f"{profile_name} — Download/Add RSS Feed",
            title_font, button_font,
            mouse_pos, clicked,
        )
        _draw_download_overlay(state, mouse_pos, clicked, events)
        return

    # --- NORMAL MODE ---
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
        _refresh_feed_items(state, force=True)

    # --- CONTENT AREA ---
    content_x = int(screen.get_width() * sidebar.SIDEBAR_WIDTH_RATIO) if state["sidebar_open"] else 20
    content_y = CONTENT_TOP + 10

    layout_stale = (
        not state["feed_item_layout"]
        or len(state["feed_item_layout"]) != len(state["feed_items"])
    )
    if layout_stale:
        _setup_item_layout(state, content_x, content_y)

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

    # --- SIDEBAR ---
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
