import pygame
import time
import os
import logging
import json
from pathlib import Path

import src.ui.components.tile as tile
import src.user.config_pipeline
import src.util.load_profiles
import src.util.make_profile

logger = logging.getLogger(__name__)

# --- Some file paths ---
SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent.parent
PROFILE_DIRECTORY = PROJECT_ROOT / "src" / "user" / "data"
USER_ICON = SCRIPT_DIR / "assets" / "user.png"
ADD_ICON = SCRIPT_DIR / "assets" / "add.png"


logger.info(f"Profile directory is {PROFILE_DIRECTORY}")

# --- Constants ---
MAX_TILES_PER_PAGE = 8

# --- Pygame setup ---
pygame.init()
screen = pygame.display.set_mode((1920, 1080))
clock = pygame.time.Clock()
running = True

font = pygame.font.SysFont(None, 24)
button_font = pygame.font.SysFont(None, 32)
button_color = (100, 100, 100)

# --- Load profiles ---
profile_data = src.util.load_profiles.load_profiles_from_directory(PROFILE_DIRECTORY)

# Build the profiles dict for the tile layout (name → color_hex)
profiles = {name: info["color_hex"] for name, info in profile_data.items()}

logger.info(f"Loaded {len(profiles)} profiles: {list(profiles.keys())}")

# --- Variables ---
current_page: int = 0
last_click_time = 0
click_cooldown = 250

# --- Layout cache ---
profile_layout = []

def setup_profiles(profile_dict, screen_w, screen_h):
    """Calculates the tile positions for the CURRENT PAGE."""
    global profile_layout
    profile_layout = []

    TILE_W, TILE_H = 310, 310
    GAP = 10
    COLS = 4

    colors = list(profile_dict.values()) + ["#00FF00"]
    names = list(profile_dict.keys()) + ["Add Profile"]

    visible_count = min(len(colors), MAX_TILES_PER_PAGE)
    row_count = (visible_count + COLS - 1) // COLS

    grid_w = (COLS * TILE_W) + ((COLS - 1) * GAP)
    grid_h = (row_count * TILE_H) + ((row_count - 1) * GAP)

    start_x = (screen_w - grid_w) // 2
    start_y = ((screen_h - grid_h) // 2) + 25

    start_index = current_page * MAX_TILES_PER_PAGE
    end_index = min(len(colors), start_index + MAX_TILES_PER_PAGE)

    for i in range(start_index, end_index):
        global_index = i
        color = colors[global_index]
        label = names[global_index]

        col = (global_index % MAX_TILES_PER_PAGE) % COLS
        row = (global_index % MAX_TILES_PER_PAGE) // COLS

        x = start_x + (col * (TILE_W + GAP))
        y = start_y + (row * (TILE_H + GAP))

        is_add = (global_index == len(colors) - 1)

        profile_layout.append([x, y, TILE_W, TILE_H, color, label, is_add, global_index])

setup_profiles(profiles, screen.get_width(), screen.get_height())

# --- Main loop ---
while running:
    mouse_x, mouse_y = pygame.mouse.get_pos()
    clicked = False
    selected_profile = None

    current_time = pygame.time.get_ticks()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if current_time - last_click_time > click_cooldown:
                    clicked = True
                    last_click_time = current_time
                else:
                    clicked = False

    screen.fill("#333333")
    mouse_pos = pygame.mouse.get_pos()

    # Draw title
    title_font = pygame.font.SysFont(None, 48)
    title_text = "SELECT PROFILE"
    title_surf = title_font.render(title_text, True, (255, 255, 255))
    title_rect = title_surf.get_rect(center=(screen.get_width() // 2, 50))
    screen.blit(title_surf, title_rect)

    # Render tiles
    for tile_data in profile_layout:
        x, y, w, h, color_hex, label, is_add, global_index = tile_data

        if x < mouse_pos[0] < x + w and y < mouse_pos[1] < y + h:
            if clicked:
                selected_profile = label

        icon_path = USER_ICON
        if is_add:
            icon_path = ADD_ICON
        tile.draw_tile(screen, x, y, "Large", color_hex, label, mouse_pos, font, clicked, icon_path)

    # Previous button
    if current_page > 0:
        prev_rect = pygame.Rect(100, 650, 150, 50)
        pygame.draw.rect(screen, button_color, prev_rect)
        prev_text = button_font.render("< Prev", True, (255, 255, 255))
        screen.blit(prev_text, prev_rect.center)
        if prev_rect.collidepoint(mouse_pos) and clicked:
            current_page -= 1
            setup_profiles(profiles, screen.get_width(), screen.get_height())

    # Next button
    total_tiles = len(profiles) + 1
    total_pages = (total_tiles + MAX_TILES_PER_PAGE - 1) // MAX_TILES_PER_PAGE
    if current_page < total_pages - 1:
        next_rect = pygame.Rect(screen.get_width() - 250, 650, 150, 50)
        pygame.draw.rect(screen, button_color, next_rect)
        next_text = button_font.render("Next >", True, (255, 255, 255))
        screen.blit(next_text, next_rect.center)
        if next_rect.collidepoint(mouse_pos) and clicked:
            current_page += 1
            setup_profiles(profiles, screen.get_width(), screen.get_height())

    # Handle clicks
    if selected_profile:
        if selected_profile == "Add Profile":
            logger.info("Adding new profile")
            name = src.util.make_profile.generate_default_profile_name() #generate a default name
            src.util.make_profile.create_empty_profile(PROFILE_DIRECTORY,name) #make a new profile
            # --- Load profiles ---
            profile_data = src.util.load_profiles.load_profiles_from_directory(PROFILE_DIRECTORY)

            # Build the profiles dict for the tile layout (name → color_hex)
            profiles = {name: info["color_hex"] for name, info in profile_data.items()}

            #Refresh UI
            setup_profiles(profiles, screen.get_width(), screen.get_height())

        else:
            # Look up the selected profile's data
            if selected_profile in profile_data:
                profile_info = profile_data[selected_profile]
                print(f"Profile {selected_profile} clicked")
                print(f"  - File: {profile_info['file_path']}")
                print(f"  - Color: {profile_info['color_hex']}")
                # Later: switch to the RSS reader view with this profile data
                # switch_to_rss_reader(profile_info['data'])
            else:
                print(f"Profile {selected_profile} clicked (data not found)")

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
