# src/ui/screens/feed_screen.py
import logging

import pygame

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

    profile_name = state["selected_profile"]
    title_surf = title_font.render(f"FEEDS - {profile_name}", True, (255, 255, 255))
    title_rect = title_surf.get_rect(center=(screen.get_width() // 2, 50))
    screen.blit(title_surf, title_rect)

    # TODO: Render your item tiles here.
    # You'll want a back button, and possibly a "by source" / "by category" layout.

    # --- BACK BUTTON ---
    button_font = state["button_font"]
    back_rect = pygame.Rect(50, 50, 150, 50)
    pygame.draw.rect(screen, state["button_color"], back_rect)
    back_text = button_font.render("< Back", True, (255, 255, 255))
    screen.blit(back_text, back_rect.center)

    if back_rect.collidepoint(mouse_pos) and clicked:
        logger.info("Returning to PROFILE_SELECT")
        state["current_screen"] = "PROFILE_SELECT"
        state["selected_profile"] = None
        # Reload the profile screen state
        from src.ui.screens import profile_select
        profile_select.init(state)
