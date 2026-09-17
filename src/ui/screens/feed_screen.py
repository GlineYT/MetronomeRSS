import logging
import pygame

from src.ui.components import button

logger = logging.getLogger(__name__)


def init(state):
    """Called once when this screen is entered."""
    # Example: load the feeds for the selected profile
    logger.info(f"Initializing feed screen for {state['selected_profile']}")
    state["feed_scroll"] = 0  # Example per-screen state



def draw(state, mouse_pos, clicked, events):
    """Draws the feed screen."""
    screen = state["screen"]
    title_font = pygame.font.SysFont(None, 48)
    button_font = state["button_font"]
    screen = state["screen"]
    accent = state.get("accent_color", state["button_color"])

    profile_name = state["selected_profile"]

    # --- TOP BAR (draw first, so it's behind everything) ---
    navbar = pygame.Rect(0, 0, screen.get_width(), 50)
    pygame.draw.rect(screen, accent, navbar)

    # --- BACK BUTTON (drawn on top of the navbar) ---
    back_button = button.draw_button(
        screen, 10, 5, "Back", button_font, mouse_pos, clicked,accent
    )
    if back_button:
        logger.info("Returning to PROFILE_SELECT")
        state["current_screen"] = "PROFILE_SELECT"
        state["selected_profile"] = None
        from src.ui.screens import profile_select
        profile_select.init(state)
        return  #stop drawing this frame's remaining content

    # --- TITLE (in the navbar, centered) ---
    title_surf = title_font.render(f"FEEDS - {profile_name}", True, (255, 255, 255))
    title_rect = title_surf.get_rect(center=(screen.get_width() // 2, 25))
    screen.blit(title_surf, title_rect)

    # --- FEED ITEMS (below the navbar) ---
    # TODO: Render your item tiles here, starting at y = 50
