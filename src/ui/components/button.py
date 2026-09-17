import pygame


def draw_button(screen, x, y, label, font, mouse_pos, clicked,
                accent_color=(255, 128, 0), height=40, defType="default"):
    """Draws a Metro UI button. Returns True if clicked."""

    text_surface = font.render(label, True, (255, 255, 255))
    text_w, text_h = text_surface.get_size()
    width = text_w + 20
    button_rect = pygame.Rect(x, y, width, height)
    is_hovered = button_rect.collidepoint(mouse_pos)

    # Override accent color based on button type
    if defType == "warning":
        accent_color = (255, 166, 0)
    elif defType == "danger":
        accent_color = (255, 20, 0)

    # Draw the background
    pygame.draw.rect(screen, accent_color, button_rect)

    # Hover border (3px)
    if is_hovered:
        pygame.draw.rect(screen, (240, 240, 240), button_rect, 3)

        if clicked:
            print(f"Button '{label}' pressed")
            return True

    # Draw the text centered
    text_x = x + (width - text_w) // 2
    text_y = y + (height - text_h) // 2
    screen.blit(text_surface, (text_x, text_y))

    return False
