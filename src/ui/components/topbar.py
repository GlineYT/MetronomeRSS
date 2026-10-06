from pathlib import Path
import pygame

from src.ui.components import tile
from src.ui.components import button


# --- Path resolution (same pattern as sidebar.py) ---
SCRIPT_DIR = Path(__file__).parent.resolve()
ASSETS_DIR = SCRIPT_DIR.parent / "assets"

def _asset(name):
    return str(ASSETS_DIR / name)


# --- Layout constants ---
TOPBAR_HEIGHT = 50
HAMBURGER_MARGIN = 10
HAMBURGER_SIZE = 30
BUTTON_Y = 5


def draw_topbar(screen, accent_color, title, title_font, button_font,
                mouse_pos, clicked,
                show_hamburger=False,
                show_back=False,
                action_buttons=None):
    """
    Draws the topbar. Returns a dict describing which interactive elements
    were interacted with this frame.

    Args:
        screen: Pygame surface
        accent_color: Theme accent color for the navbar background
        title: The text to display, centered
        title_font: Font for the title
        button_font: Font for action buttons (and the back button)
        mouse_pos: Current mouse position
        clicked: Whether a click was registered this frame
        show_hamburger: If True, draw the hamburger toggle on the left
        show_back: If True, draw a "Back" button on the left
        action_buttons: List of (label, action_key) tuples to render on the right.
                        Each button is returned as clicked in the result dict.

    Returns:
        A dict with keys:
            "hamburger": True if the hamburger was clicked
            "back": True if the back button was clicked
            "actions": dict mapping action_key -> True/False
    """
    result = {
        "hamburger": False,
        "back": False,
        "actions": {},
    }

    screen_w = screen.get_width()

    # --- BACKGROUND ---
    navbar = pygame.Rect(0, 0, screen_w, TOPBAR_HEIGHT)
    pygame.draw.rect(screen, accent_color, navbar)

    # --- LEFT SIDE: HAMBURGER or BACK ---
    left_cursor = HAMBURGER_MARGIN

    if show_hamburger:
        # Draw the hamburger icon (three horizontal lines)
        toggle_rect = pygame.Rect(left_cursor, HAMBURGER_MARGIN, HAMBURGER_SIZE, HAMBURGER_SIZE)
        if toggle_rect.collidepoint(mouse_pos):
            pygame.draw.rect(screen, (255, 255, 255), toggle_rect, 2)
        for j in range(3):
            pygame.draw.rect(
                screen, (255, 255, 255),
                (toggle_rect.x + 4, toggle_rect.y + 5 + j * 8, 22, 3)
            )
        if toggle_rect.collidepoint(mouse_pos) and clicked:
            result["hamburger"] = True

        left_cursor += HAMBURGER_SIZE + 15

    if show_back:
        back_rect = button.draw_button(
            screen, left_cursor, BUTTON_Y, "Back", button_font,
            mouse_pos, clicked, accent_color
        )
        if back_rect:
            result["back"] = True
        # Note: your button component may render with its own accent color;
        # tweak the call to match your signature.

    # --- CENTER: TITLE ---
    title_surf = title_font.render(title, True, (255, 255, 255))
    title_rect = title_surf.get_rect(center=(screen_w // 2, TOPBAR_HEIGHT // 2))
    screen.blit(title_surf, title_rect)

    # --- RIGHT SIDE: ACTION BUTTONS ---
    if action_buttons:
        # Lay them out from right to left
        right_cursor = screen_w - 15
        for label, action_key in reversed(action_buttons):
            # Measure the button width by rendering the label
            label_surf = button_font.render(label, True, (255, 255, 255))
            btn_w = label_surf.get_width() + 20   # 10px padding each side

            btn_x = right_cursor - btn_w
            btn_clicked = button.draw_button(
                screen, btn_x, BUTTON_Y, label, button_font,
                mouse_pos, clicked, accent_color
            )
            if btn_clicked:
                result["actions"][action_key] = True

            # Move cursor left past this button, plus a small gap
            right_cursor = btn_x - 10

    return result
