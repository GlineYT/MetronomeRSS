# src/ui/components/modal.py
from pathlib import Path
import pygame

from src.ui.components import ptext
from src.ui.components import tile


# --- Path resolution ---
SCRIPT_DIR = Path(__file__).parent.resolve()
ASSETS_DIR = SCRIPT_DIR.parent / "assets"

def _asset(name):
    return str(ASSETS_DIR / name)


# --- Layout constants (all independent now) ---
# The "modal area" is a virtual region we use for centering. There's no box drawn for it.
MODAL_AREA_WIDTH = 750
MODAL_AREA_HEIGHT = 700
MODAL_PADDING = 10

# Title bar
TITLE_BAR_HEIGHT = 75
TITLE_BAR_WIDTH = 900      # independent of the X button now

# Metadata column
METADATA_TILE_SIZE = 100
METADATA_TILE_GAP = 0
METADATA_COLUMN_WIDTH = 350   # icon + value space

# Description panel
DESCRIPTION_WIDTH = 500
DESCRIPTION_HEIGHT = 390

# X button (screen-anchored, not modal-anchored)
X_BUTTON_SIZE = 75
X_BUTTON_MARGIN = 20


# --- Metadata fields ---
META_FIELDS = [
    ("source", _asset("rss.png")),
    ("link",   _asset("link.png")),
    ("time",   _asset("clock.png")),
    ("date",   _asset("calendar.png")),
]


def draw_modal(screen, title, description, metadata, mouse_pos, clicked, accent_color,
               scroll_speed=80.0, pause_duration=0.5):
    """
    Draws the modal. No superbox — just three independent floating pieces:
    1. Title bar (top, centered in the modal area)
    2. Metadata column (left)
    3. Description panel (right)

    Returns:
        (is_closed: bool, modal_rect: pygame.Rect)
    """
    # --- DIM BACKGROUND ---
    dim_surface = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    dim_surface.fill((0, 0, 0, 120))
    screen.blit(dim_surface, (0, 0))

    screen_w, screen_h = screen.get_size()

    # Virtual modal area center (used only for positioning)
    area_x = (screen_w - MODAL_AREA_WIDTH) // 2
    area_y = (screen_h - MODAL_AREA_HEIGHT) // 2

    # --- TITLE BAR (independent rectangle) ---
    title_bar_rect = pygame.Rect(
        area_x + (MODAL_AREA_WIDTH - TITLE_BAR_WIDTH) // 2 + 35,
        area_y,
        TITLE_BAR_WIDTH,
        TITLE_BAR_HEIGHT,
    )

    pygame.draw.rect(screen, (34, 34, 34), title_bar_rect)
    pygame.draw.rect(screen, (51, 51, 51), title_bar_rect, 3)

    # --- MARQUEE TITLE ---
    title_font = pygame.font.SysFont("Arial", 32, bold=True)
    title_surface = title_font.render(title, True, accent_color)
    title_width = title_surface.get_width()
    title_y = title_bar_rect.y + (title_bar_rect.h - title_surface.get_height()) // 2

    old_clip = screen.get_clip()
    screen.set_clip(title_bar_rect.inflate(-6, -6))  # inset to sit inside the border

    if title_width > title_bar_rect.w:
        total_travel = title_bar_rect.w + title_width
        pause_pixels = int(pause_duration * scroll_speed)
        cycle = total_travel + pause_pixels * 2

        elapsed = pygame.time.get_ticks() / 1000.0
        t = int((elapsed * scroll_speed) % cycle)

        if t < pause_pixels:
            actual_offset = 0
        elif t < pause_pixels + total_travel:
            actual_offset = t - pause_pixels
        else:
            actual_offset = total_travel

        draw_x = title_bar_rect.x - title_width + actual_offset
    else:
        draw_x = title_bar_rect.x + (title_bar_rect.w - title_width) // 2

    screen.blit(title_surface, (draw_x, title_y))
    screen.set_clip(old_clip)

    # --- X BUTTON (screen-anchored, top-right corner) ---
    x_pos = (screen_w - X_BUTTON_SIZE - X_BUTTON_MARGIN, X_BUTTON_MARGIN)
    x_hit_rect = pygame.Rect(x_pos[0], x_pos[1], X_BUTTON_SIZE, X_BUTTON_SIZE)

    tile.draw_tile(
        screen, x_pos[0], x_pos[1], "Small", accent_color,
        "", mouse_pos, None, clicked, _asset("xsymbol.png"),
    )

    is_closed = x_hit_rect.collidepoint(mouse_pos) and clicked

    # --- TWO-COLUMN BODY BELOW THE TITLE ---
    body_y = title_bar_rect.bottom + MODAL_PADDING

    # --- METADATA COLUMN (left side) ---
    meta_x = area_x
    meta_y = body_y

    for key, icon_path in META_FIELDS:
        value = metadata.get(key, "")
        if not value:
            continue

        value_font = pygame.font.SysFont("Arial", 24)
        value_surface = value_font.render(value, True, accent_color)

        # --- ROW BOX (background + border) ---
        # Fixed row height = tile height + small vertical padding
        ROW_PADDING = 10
        row_height = 100
        row_width = METADATA_COLUMN_WIDTH + 40
        row_rect = pygame.Rect(
            meta_x - 40,
            meta_y + 10 - ROW_PADDING,
            row_width,
            row_height - ROW_PADDING,
        )
        pygame.draw.rect(screen, (34, 34, 34), row_rect)          # #222
        pygame.draw.rect(screen, (51, 51, 51), row_rect, 3)       # #333 border

        # --- ICON TILE ---
        tile.draw_tile(
            screen, meta_x - 34, meta_y + ROW_PADDING - 3, "Small", accent_color,
            "", (-1, -1), None, False, icon_path,
        )

        # --- VALUE TEXT ---
        value_x = meta_x + METADATA_TILE_SIZE - 50
        value_y = meta_y + (METADATA_TILE_SIZE - value_surface.get_height()) // 2 - 5

        value_clip = pygame.Rect(
            value_x, value_y,
            METADATA_COLUMN_WIDTH - METADATA_TILE_SIZE - 10,
            value_surface.get_height(),
        )
        screen.set_clip(value_clip)
        screen.blit(value_surface, (value_x, value_y))
        screen.set_clip(old_clip)

        meta_y += METADATA_TILE_SIZE + METADATA_TILE_GAP

    # --- DESCRIPTION PANEL (right side, independent size) ---
    desc_x = area_x + METADATA_COLUMN_WIDTH + MODAL_PADDING
    desc_y = body_y
    desc_w = DESCRIPTION_WIDTH
    desc_h = DESCRIPTION_HEIGHT

    desc_rect = pygame.Rect(desc_x, desc_y, desc_w, desc_h)
    pygame.draw.rect(screen, (34, 34, 34), desc_rect)
    pygame.draw.rect(screen, (51, 51, 51), desc_rect, 3)

    # Content clip (inset from the border)
    content_rect = desc_rect.inflate(-12, -12)
    screen.set_clip(content_rect)

    ptext.draw(
        description,
        surf=screen,
        top=content_rect.y,
        left=content_rect.x,
        sysfontname="Arial",
        fontsize=20,
        color=(255, 255, 255),
        width=content_rect.w - 10,
        lineheight=1.4,
    )
    screen.set_clip(old_clip)

    # --- SCROLLBAR THUMB (accent-colored, right edge of desc panel) ---
    thumb_width = 6
    thumb_rect = pygame.Rect(
        desc_rect.right - thumb_width - 6,
        desc_rect.y + 12,
        thumb_width,
        120,
    )
    pygame.draw.rect(screen, accent_color, thumb_rect)

    # The "modal_rect" returned to the caller is only used for input gating
    # (i.e., is the click inside the modal?). We return a bounding rect that
    # covers everything: title bar, metadata column, and description panel.
    # This gives a clean "click outside to close" region.
    bounding_left = min(title_bar_rect.left, desc_rect.left, meta_x)
    bounding_right = max(title_bar_rect.right, desc_rect.right)
    bounding_top = title_bar_rect.top
    bounding_bottom = max(desc_rect.bottom, meta_y)

    modal_bounds = pygame.Rect(
        bounding_left,
        bounding_top,
        bounding_right - bounding_left,
        bounding_bottom - bounding_top,
    )

    return is_closed, modal_bounds
