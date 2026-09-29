from src.ui.components import ptext
import pygame


def draw_item_tile(screen, x, y, title, description, mouse_pos, clicked, accent_color=(100, 149, 237), size=300):
    tile_rect = pygame.Rect(x, y, size, size)
    is_hovered = tile_rect.collidepoint(mouse_pos)

    was_clicked = False
    if is_hovered and clicked:
        was_clicked = True

    tile_color = (40, 40, 40)
    pygame.draw.rect(screen, tile_color, tile_rect)

    if is_hovered:
        pygame.draw.rect(screen, (240, 240, 240), tile_rect, 3)

    title_bottom = y + 10  # Default if title is empty

    # --- 1. FIRST CLIP: Draw the title ---
    old_clip = screen.get_clip()
    screen.set_clip(tile_rect.inflate(-6, -6))

    title_surf, title_pos = ptext.draw(
        title,
        surf=screen,
        pos=(x + 10, y + 10),
        sysfontname="Arial",
        fontsize=28,
        color=(255, 255, 255),
        bold=True,
        width=size - 20,
        lineheight=1.2
    )
    title_bottom = title_pos[1] + title_surf.get_height() + 10

    # --- 2. SECOND CLIP: Draw the description ---
    # The description box is the remaining area below the title.
    desc_box = pygame.Rect(x, title_bottom, size, y + size - title_bottom)
    screen.set_clip(desc_box.inflate(-6, -6))

    # Anchor to TOP (not bottom) so overflow spills off the bottom of the tile.
    ptext.draw(
        description,
        surf=screen,
        top=title_bottom,       #Anchor to top of description area
        left=x + 10,
        sysfontname="Arial",
        fontsize=22,
        color=(200, 200, 200),
        width=size - 20,
        lineheight=1.2
    )

    # --- RESTORE THE ORIGINAL CLIP ---
    screen.set_clip(old_clip)

    if was_clicked:
        print(f"Item tile clicked: {title}")

    return was_clicked
