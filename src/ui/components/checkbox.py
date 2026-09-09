# components/checkbox.py
import pygame

def draw_checkbox(screen, x, y, label, state_dict, key, font, mouse_pos, clicked, accent_color=(100, 149, 237), size=25):
    """Draws a checkbox. Returns True if state was toggled."""

    # Ensure the state exists (default to False if not set)
    if key not in state_dict:
        state_dict[key] = False

    checkbox_rect = pygame.Rect(x, y, size, size)
    is_hovered = checkbox_rect.collidepoint(mouse_pos)

    # 1. Draw the background (white if not checked, accent color if checked)
    if state_dict[key]:
        pygame.draw.rect(screen, accent_color, checkbox_rect)
    else:
        pygame.draw.rect(screen, (255, 255, 255), checkbox_rect)

    # 2. Draw the hover border (3px, 240, 240, 240)
    if is_hovered:
        pygame.draw.rect(screen, (240, 240, 240), checkbox_rect, 3)

    # 3. Draw the checkmark (only if checked) - use a thick line
    if state_dict[key]:
        # Draw a simple checkmark using a thick line
        pygame.draw.line(screen, (255, 255, 255), (x + 6, y + 12), (x + 11, y + 17), 4)
        pygame.draw.line(screen, (255, 255, 255), (x + 11, y + 16), (x + 18, y + 7), 4)

    # 4. Draw the label to the right of the checkbox
    if label:
        text_surface = font.render(label, True, (255, 255, 255))
        screen.blit(text_surface, (x + size + 10, y + (size - text_surface.get_height()) // 2))

    # 5. Handle the click event (toggle the state)
    if is_hovered and clicked:
        state_dict[key] = not state_dict[key]
        return True  # State was toggled

    return False
