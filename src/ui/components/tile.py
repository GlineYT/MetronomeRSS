import os

import pygame


def draw_tile(screen, x, y, size, color, label, mouse_pos, font, is_clicked, icon_path=None):
    draw_text = True

    if size == "Large":
        w, h = 310, 310
        icon_size = 256
    elif size == "Wide":
        w, h = 310, 150
        icon_size = 128
    elif size == "Medium":
        w, h = 150, 150
        icon_size = 128
    elif size == "Small":
        w, h = 75, 75
        draw_text = False
        icon_size = 64

    # 1. Draw the base tile color
    pygame.draw.rect(screen, color, (x, y, w, h))

    # 2. Check if the mouse is hovering
    is_hovered = x < mouse_pos[0] < x + w and y < mouse_pos[1] < y + h

    if is_hovered:
        # --- THE FROSTED OVERLAY ---
        # Create a transparent surface just for the tile
        overlay = pygame.Surface((w, h), pygame.SRCALPHA)

        # Fill it with a semi-transparent white (e.g., 40 out of 255 = ~15% opacity)
        # You can tweak this: higher alpha = more "frost"
        overlay.fill((255, 255, 255, 40))

        # Blit the overlay onto the tile
        screen.blit(overlay, (x, y))

        # Draw the 240, 240, 240 border on top
        pygame.draw.rect(screen, (240, 240, 240), (x, y, w, h), 3)

    # 3. Draw the Icon (Centered)
    if icon_path and os.path.exists(icon_path):
        icon = pygame.image.load(icon_path).convert_alpha()
        icon_w, icon_h = icon.get_size()
        scale = min(icon_size / icon_w, icon_size / icon_h)
        new_w = int(icon_w * scale)
        new_h = int(icon_h * scale)
        icon = pygame.transform.scale(icon, (new_w, new_h))

        icon_x = x + (w - new_w) // 2
        icon_y = y + (h - new_h) // 2
        screen.blit(icon, (icon_x, icon_y))

    # 4. Draw the text
    if draw_text:
        img = font.render(label, True, (255, 255, 255))
        if size != "Large":
            screen.blit(img, (x + 5, y + h - 15))
        else:
            screen.blit(img, (x + 5, y + h - 16))

    return is_clicked
