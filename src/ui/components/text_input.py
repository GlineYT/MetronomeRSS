import pygame

def draw_text_input(screen, x, y, width, font, mouse_pos, clicked, events, text_buffer, accent_color=(100, 149, 237), height=50):
    """
    Draws a Metro UI text input.
    Returns:
        str or None: Returns the string when Enter is pressed, else None.
    """
    global input_focus_state
    if 'input_focus_state' not in globals():
        input_focus_state = {} # Store focus by 'id' or pointer

    input_id = (x, y)

    if input_id not in input_focus_state:
        input_focus_state[input_id] = False

    input_rect = pygame.Rect(x, y, width, height)
    is_hovered = input_rect.collidepoint(mouse_pos)

    # --- FOCUS HANDLING ---
    if clicked:
        if is_hovered:
            for key in input_focus_state:
                input_focus_state[key] = False
            input_focus_state[input_id] = True
        else:
            input_focus_state[input_id] = False

    active = input_focus_state[input_id]

    # --- INPUT HANDLING (Only if active) ---
    result = None
    if active:
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    if len(text_buffer[0]) > 0:
                        text_buffer[0] = text_buffer[0][:-1]
                elif event.key == pygame.K_RETURN:
                    result = text_buffer[0]  # Return the current text
                    text_buffer[0] = ""      # Reset the buffer
                    input_focus_state[input_id] = False
                else:
                    text_buffer[0] += event.unicode

    # --- DRAWING ---
    pygame.draw.rect(screen, (255, 255, 255), input_rect)

    border_color = (200, 200, 200)
    if active:
        border_color = accent_color

    pygame.draw.rect(screen, border_color, input_rect, 3)

    # --- TEXT RENDERING WITH CLIPPING ---
    text_surface = font.render(text_buffer[0], True, (0, 0, 0))

    text_width = text_surface.get_width()
    max_visible_width = width - 20

    if text_width > max_visible_width:
        overflow = text_width - max_visible_width
        text_x = x + 10 - overflow
    else:
        text_x = x + 10

    text_y = y + (height - text_surface.get_height()) // 2

    # Save the current clip area
    old_clip = screen.get_clip()
    screen.set_clip(input_rect.inflate(-6, -6))

    # Draw the text
    screen.blit(text_surface, (text_x, text_y))

    # --- BLINKING CURSOR ---
    if active:
        # Blink every 500ms
        if (pygame.time.get_ticks() // 500) % 2 == 0:
            # Calculate the X position of the cursor (at the end of the visible text)
            cursor_x = text_x + text_width + 1  # 1px offset to the right
            cursor_y = y + 10  # 10px from top
            cursor_height = height - 20  # Leave 10px padding at bottom

            # Ensure cursor stays inside the input box (visible area)
            if cursor_x < x + width - 5:
                pygame.draw.rect(screen, (0, 0, 0), (cursor_x, cursor_y, 2, cursor_height))

    # Restore the clip area
    screen.set_clip(old_clip)

    return result
