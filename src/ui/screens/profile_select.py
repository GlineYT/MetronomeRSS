# src/ui/screens/profile_select.py
import logging

import pygame

import src.util.load_profiles
import src.util.make_profile
from src.ui.components import text_input, tile

logger = logging.getLogger(__name__)

# --- Constants ---
MAX_TILES_PER_PAGE = 8
TILE_W, TILE_H = 310, 310
GAP = 10
COLS = 4


def _setup_profiles(state, screen_w, screen_h):
    """Calculates tile positions for the current page and stores them in state."""
    profile_dict = state["profiles"]
    profile_layout = []

    colors = list(profile_dict.values()) + ["#00FF00"]
    names = list(profile_dict.keys()) + ["Add Profile"]

    visible_count = min(len(colors), MAX_TILES_PER_PAGE)
    row_count = (visible_count + COLS - 1) // COLS

    grid_w = (COLS * TILE_W) + ((COLS - 1) * GAP)
    grid_h = (row_count * TILE_H) + ((row_count - 1) * GAP)

    start_x = (screen_w - grid_w) // 2
    start_y = ((screen_h - grid_h) // 2) + 25

    start_index = state["current_page"] * MAX_TILES_PER_PAGE
    end_index = min(len(colors), start_index + MAX_TILES_PER_PAGE)

    for i in range(start_index, end_index):
        color = colors[i]
        label = names[i]

        col = (i % MAX_TILES_PER_PAGE) % COLS
        row = (i % MAX_TILES_PER_PAGE) // COLS

        x = start_x + (col * (TILE_W + GAP))
        y = start_y + (row * (TILE_H + GAP))

        is_add = (i == len(colors) - 1)
        profile_layout.append([x, y, TILE_W, TILE_H, color, label, is_add])

    state["profile_layout"] = profile_layout


def _refresh_profiles(state):
    """Reloads profiles from disk and rebuilds the layout."""
    profile_data = src.util.load_profiles.load_profiles_from_directory(state["profile_directory"])
    state["profile_data"] = profile_data
    state["profiles"] = {name: info["color_hex"] for name, info in profile_data.items()}
    _setup_profiles(state, state["screen"].get_width(), state["screen"].get_height())


def init(state):
    """Called once when this screen is entered. Resets per-screen state."""
    state["current_page"] = 0
    state["adding_profile"] = False
    state["text_buffer"] = [""]
    state["add_profile_error"] = None
    _refresh_profiles(state)


def draw(state, mouse_pos, clicked, events):
    """Draws the profile screen and handles its interactions."""
    screen = state["screen"]
    font = state["font"]
    button_font = state["button_font"]
    button_color = state["button_color"]
    user_icon = state["user_icon"]
    add_icon = state["add_icon"]

    title_font = pygame.font.SysFont(None, 48)
    title_surf = title_font.render("SELECT PROFILE", True, (255, 255, 255))
    title_rect = title_surf.get_rect(center=(screen.get_width() // 2, 50))
    screen.blit(title_surf, title_rect)

    selected_profile = None

    # --- RENDER TILES ---
    for tile_data in state["profile_layout"]:
        x, y, w, h, color_hex, label, is_add = tile_data

        if x < mouse_pos[0] < x + w and y < mouse_pos[1] < y + h and clicked:
                selected_profile = label

        icon_path = add_icon if is_add else user_icon
        tile.draw_tile(screen, x, y, "Large", color_hex, label, mouse_pos, font, clicked, icon_path)

    # --- PAGINATION ---
    if state["current_page"] > 0:
        prev_rect = pygame.Rect(100, 900, 150, 50)
        pygame.draw.rect(screen, button_color, prev_rect)
        prev_text = button_font.render("< Prev", True, (255, 255, 255))
        screen.blit(prev_text, prev_rect.center)
        if prev_rect.collidepoint(mouse_pos) and clicked:
            state["current_page"] -= 1
            _setup_profiles(state, screen.get_width(), screen.get_height())

    total_tiles = len(state["profiles"]) + 1
    total_pages = (total_tiles + MAX_TILES_PER_PAGE - 1) // MAX_TILES_PER_PAGE
    if state["current_page"] < total_pages - 1:
        next_rect = pygame.Rect(screen.get_width() - 250, 900, 150, 50)
        pygame.draw.rect(screen, button_color, next_rect)
        next_text = button_font.render("Next >", True, (255, 255, 255))
        screen.blit(next_text, next_rect.center)
        if next_rect.collidepoint(mouse_pos) and clicked:
            state["current_page"] += 1
            _setup_profiles(state, screen.get_width(), screen.get_height())

    # --- CLICK HANDLING ---
    if selected_profile:
        if selected_profile == "Add Profile":
            logger.info("Adding new profile")
            state["adding_profile"] = True
            state["text_buffer"][0] = ""
        else:
            # Switch to the feed screen for this profile!
            logger.info(f"Switching to FEEDS screen for {selected_profile}")
            state["selected_profile"] = selected_profile
            state["current_screen"] = "FEEDS"
            init_feed_screen = src.ui.screens.feed_screen.init
            init_feed_screen(state)

    # --- ADD PROFILE OVERLAY ---
    if state["adding_profile"]:
        dim = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        dim.fill((0, 0, 0, 150))
        screen.blit(dim, (0, 0))

        prompt_surf = button_font.render("Enter a name for your new profile:", True, (255, 255, 255))
        screen.blit(prompt_surf, (800, 700))

        result = text_input.draw_text_input(
            screen, 800, 760, 320, font, mouse_pos, clicked, events,
            state["text_buffer"], placeholder="Profile name..."
        )

        # --- ERROR MESSAGE (if one was set last frame) ---
        if state.get("add_profile_error"):
            error_surf = font.render(state["add_profile_error"], True, (255, 100, 100))
            screen.blit(error_surf, (800, 825))

        if result is not None and result.strip() != "":
            # --- DUPLICATE NAME CHECK ---
            cleaned_name = result.strip()

            if cleaned_name in state["profiles"]:
                # Name is taken! Show error, keep the input open.
                logger.warning(f"Profile name '{cleaned_name}' already exists!")
                state["add_profile_error"] = "That name is already taken. Try another."
                state["text_buffer"][0] = ""  # Clear input so they can retype
            else:
                # Name is unique - create the profile
                logger.info(f"Creating profile: {cleaned_name}")
                src.util.make_profile.create_empty_profile(state["profile_directory"], cleaned_name)
                _refresh_profiles(state)
                state["adding_profile"] = False
                state["add_profile_error"] = None
                state["text_buffer"][0] = ""
