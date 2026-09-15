import components.ptext
import pygame


def draw_modal(screen, title, description, mouse_pos, clicked, accent_color=(100, 149, 237)):
    """
    Draws a modal popup over the screen. Returns True if closed (X clicked).
    """
    # --- STAGE 1: DIM THE BACKGROUND ---
    dim_surface = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    dim_surface.fill((0, 0, 0, 180))  # 180 alpha = dark but not fully opaque
    screen.blit(dim_surface, (0, 0))

    # --- STAGE 2: THE MODAL WINDOW (Fixed size) ---
    modal_width, modal_height = 600, 800
    screen_w, screen_h = screen.get_size()
    modal_x = (screen_w - modal_width) // 2
    modal_y = (screen_h - modal_height) // 2

    modal_rect = pygame.Rect(modal_x, modal_y, modal_width, modal_height)

    # Draw the modal background (use accent color or a solid dark grey)
    modal_bg_color = (40, 40, 40)
    pygame.draw.rect(screen, modal_bg_color, modal_rect)

    # Modal border (no hover border, just a clean 2px grey)
    pygame.draw.rect(screen, (240, 240, 240), modal_rect, 2)

    # --- STAGE 3: TITLE (Top left) ---
    # Clip to the modal so text doesn't leak out
    old_clip = screen.get_clip()
    screen.set_clip(modal_rect.inflate(-4, -4))

    components.ptext.draw(
        title,
        surf=screen,
        pos=(modal_x + 20, modal_y + 20),
        sysfontname="Arial",
        fontsize=36,
        color=(255, 255, 255),
        bold=True,
        width=modal_width - 100,
        lineheight=1.2
    )

    # --- STAGE 4: DESCRIPTION (Fixed gap between title and body) ---
    # Instead of centering, we just start it below the title with a specific gap
    TITLE_BODY_GAP = 20
    description_y = modal_y + 100 + TITLE_BODY_GAP  # 70 is initial title height, then add gap

    components.ptext.draw(
        description,
        surf=screen,
        left=modal_x + 20,
        top=description_y,
        sysfontname="Arial",
        fontsize=24,
        color=(200, 200, 200),
        width=modal_width - 40,
        lineheight=1.5
    )

    # --- STAGE 5: THE X BUTTON (Top Right) ---
    x_size = 30
    x_rect = pygame.Rect(modal_x + modal_width - x_size - 10, modal_y + 10, x_size, x_size)

    pygame.draw.rect(screen, (60, 60, 60), x_rect)

    pygame.draw.line(screen, (255, 255, 255), (x_rect.x + 6, x_rect.y + 6), (x_rect.x + x_size - 6, x_rect.y + x_size - 6), 3)
    pygame.draw.line(screen, (255, 255, 255), (x_rect.x + x_size - 6, x_rect.y + 6), (x_rect.x + 6, x_rect.y + x_size - 6), 3)

    is_closed = False
    if x_rect.collidepoint(mouse_pos) and clicked:
        is_closed = True
        print("Modal X clicked!")

    screen.set_clip(old_clip)

    return is_closed,modal_rect
