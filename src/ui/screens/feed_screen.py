import logging
import pygame

from src.ui.components import button
from src.ui.components import sidebar

logger = logging.getLogger(__name__)


def init(state):
    logger.info(f"Initializing feed screen for {state['selected_profile']}")
    state["feed_scroll"] = 0
    state["sidebar_open"] = False  # Start closed, or True if you prefer
    state["selected_section"] = "All RSS feeds"


def draw(state, mouse_pos, clicked, events):
    """Draws the feed screen."""
    screen = state["screen"]
    title_font = pygame.font.SysFont(None, 48)
    button_font = state["button_font"]
    small_font = state["font"]
    accent = state.get("accent_color", state["button_color"])

    profile_name = state["selected_profile"]

    # --- TOP BAR (full width, always visible behind the sidebar) ---
    navbar = pygame.Rect(0, 0, screen.get_width(), 50)
    pygame.draw.rect(screen, accent, navbar)

    # --- HAMBURGER TOGGLE (top-left) ---
    # Simple hand-drawn hamburger: three horizontal lines
    toggle_rect = pygame.Rect(10, 10, 30, 30)
    if toggle_rect.collidepoint(mouse_pos):
        pygame.draw.rect(screen, (255, 255, 255), toggle_rect, 2)  # hover border
    for j in range(3):
        pygame.draw.rect(screen, (255, 255, 255), (14, 15 + j * 8, 22, 3))
    if toggle_rect.collidepoint(mouse_pos) and clicked:
        state["sidebar_open"] = not state["sidebar_open"]

    # --- BACK BUTTON (next to the toggle) ---
    back_button = button.draw_button(
        screen, 55, 5, "Back", button_font, mouse_pos, clicked, accent
    )
    if back_button and state["sidebar_open"] == False:
        logger.info("Returning to PROFILE_SELECT")
        state["current_screen"] = "PROFILE_SELECT"
        state["selected_profile"] = None
        from src.ui.screens import profile_select
        profile_select.init(state)
        return

    # --- TITLE (centered) ---
    section = state.get("selected_section", "All RSS feeds")
    title_surf = title_font.render(f"{profile_name} — {section}", True, (255, 255, 255))
    title_rect = title_surf.get_rect(center=(screen.get_width() // 2, 25))
    screen.blit(title_surf, title_rect)

    # --- FEED ITEMS (below navbar) ---
    # TODO: Render your item tiles here, starting at y = 50

    # --- SIDEBAR (drawn LAST, on top of everything, with its own dim) ---
    sidebar_result = sidebar.draw_sidebar(
        screen, button_font, small_font,
        mouse_pos, clicked, state["sidebar_open"], accent,
    )

    if sidebar_result == "CLOSE":
        state["sidebar_open"] = False
    elif sidebar_result == "Quit":
        state["running"] = False
    elif sidebar_result:
        logger.info(f"Sidebar item clicked: {sidebar_result}")
        state["selected_section"] = sidebar_result
