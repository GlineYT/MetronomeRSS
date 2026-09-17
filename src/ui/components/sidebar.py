import pygame
import src.ui.components.tile as tile


# --- Sidebar layout constants ---
SIDEBAR_WIDTH_RATIO = 0.20   # 20% of screen width
TILE_SIZE = 75               # Matches the "Small" size in tile.py
TILE_GAP = 6
ROW_PADDING = 8
TEXT_PAD_LEFT = 24

# --- Menu items (label, subtitle, icon_path) ---
MENU_ITEMS = [
    ("All RSS feeds", "See everything",         "assets/rss.png"),
    ("Categories",    "See by category",        "assets/categories.png"),
    ("Favourites",    "See your favourites",    "assets/star.png"),
    ("Sources",       "See by source",          "assets/source.png"),
    ("Manage RSS",    "Manage your feeds",      "assets/manage.png"),
    ("Settings",      "Manage your experience", "assets/settings.png"),
    ("Quit",          "Exit Metronome RSS",     "assets/quit.png"),
]


def draw_sidebar(screen, font, small_font, mouse_pos, clicked, is_open, accent_color):
    """
    Draws the sidebar as a slide-in overlay. Dims the rest of the screen.

    Args:
        screen: Pygame surface
        font: Font for the main title text
        small_font: Font for the subtitle text
        mouse_pos: Current mouse position
        clicked: Whether a click was registered this frame
        is_open: Whether the sidebar should be visible
        accent_color: Hex string or RGB tuple for the tile color (theme)

    Returns:
        str or None: The label of the clicked menu item.
        "CLOSE" is returned if the user clicks outside the sidebar.
    """
    if not is_open:
        return None

    screen_w, screen_h = screen.get_size()
    sidebar_width = int(screen_w * SIDEBAR_WIDTH_RATIO)

    # --- DIM OVERLAY (covers everything NOT covered by the sidebar) ---
    # We only dim the area to the right of the sidebar so we don't double-darken.
    dim_overlay = pygame.Surface((screen_w - sidebar_width, screen_h), pygame.SRCALPHA)
    dim_overlay.fill((0, 0, 0, 140))  # 140 alpha = noticeable but not opaque
    screen.blit(dim_overlay, (sidebar_width, 0))

    # --- SIDEBAR BACKGROUND ---
    sidebar_rect = pygame.Rect(0, 0, sidebar_width, screen_h)
    pygame.draw.rect(screen, (30, 30, 30), sidebar_rect)

    clicked_item = None

    # --- MENU ITEMS ---
    for i, (label, subtitle, icon_path) in enumerate(MENU_ITEMS):
        row_y = i * (TILE_SIZE + TILE_GAP + ROW_PADDING * 2)
        tile_x = ROW_PADDING
        tile_y = row_y + ROW_PADDING

        row_height = TILE_SIZE + ROW_PADDING * 2
        row_rect = pygame.Rect(0, row_y, sidebar_width, row_height)
        is_hovered = row_rect.collidepoint(mouse_pos)

        # Hover highlight for the row (subtle background)
        if is_hovered:
            pygame.draw.rect(screen, (50, 50, 50), row_rect)

        # Draw the small icon tile
        tile.draw_tile(
            screen, tile_x, tile_y, "Small",
            accent_color, "", mouse_pos, font, clicked, icon_path
        )

        if is_hovered and clicked:
            clicked_item = label

        # --- Title text ---
        title_surf = font.render(label, True, (255, 255, 255))
        title_y = tile_y + (TILE_SIZE // 2) - title_surf.get_height() - 2
        screen.blit(title_surf, (tile_x + TILE_SIZE + TEXT_PAD_LEFT, title_y))

        # --- Subtitle text ---
        subtitle_surf = small_font.render(subtitle, True, (170, 170, 170))
        subtitle_y = title_y + title_surf.get_height() + 4
        screen.blit(subtitle_surf, (tile_x + TILE_SIZE + TEXT_PAD_LEFT, subtitle_y))

    # --- CLICK OUTSIDE TO CLOSE ---
    # If the user clicked but not on any item, AND the mouse is to the right of
    # the sidebar, treat it as a "close" action.
    if clicked and clicked_item is None:
        if mouse_pos[0] > sidebar_width:
            return "CLOSE"

    return clicked_item
