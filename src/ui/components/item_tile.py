import pygame
import components.ptext

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

    # Initialize the width and height of the wrapped title to 0
    title_bottom = y + 10  # Default if title is empty

    # --- 1. FIRST CLIP: Draw the title ----
    old_clip = screen.get_clip()
    # Clip to the whole tile (minus 6px)
    screen.set_clip(tile_rect.inflate(-6, -6))

    # Render the title to get its actual height (we need this to know where the description starts)
    # We'll use a "dummy" surface to measure, or just use ptext.draw and let it find its own height
    # The trick: use the return value of ptext.draw() to see where it ended.
    title_surf, title_pos = components.ptext.draw(
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
    # The title is drawn. Now we know its bottom edge.
    title_bottom = title_pos[1] + title_surf.get_height() + 10  # Add 10px gap

    # --- 2. SECOND CLIP: Draw the description ---
    # Create a sub-box for the description that stops right below the title.
    desc_box = pygame.Rect(x, title_bottom, size, y + size - title_bottom)

    # Change the clip to ONLY that sub-box.
    screen.set_clip(desc_box.inflate(-6, -6))

    components.ptext.draw(
        description,
        surf=screen,
        left=x + 10,
        bottom=y + size - 10,  # Glued to bottom of tile
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
