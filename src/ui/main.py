# src/ui/main.py
import pygame
import logging
from pathlib import Path

import src.ui.screens.profile_select as profile_select
import src.ui.screens.feed_screen as feed_screen
import src.util.load_profiles

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO,)

# --- File paths ---
SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent.parent
PROFILE_DIRECTORY = PROJECT_ROOT / "src" / "user" / "data"
USER_ICON = SCRIPT_DIR / "assets" / "user.png"
ADD_ICON = SCRIPT_DIR / "assets" / "add.png"

# --- Pygame setup ---
pygame.init()
screen = pygame.display.set_mode((1920, 1080))
clock = pygame.time.Clock()
running = True

font = pygame.font.SysFont(None, 24)
button_font = pygame.font.SysFont(None, 32)
button_color = (100, 100, 100)

# --- Load profiles once ---
profile_data = src.util.load_profiles.load_profiles_from_directory(PROFILE_DIRECTORY)
profiles = {name: info["color_hex"] for name, info in profile_data.items()}
logger.info(f"Loaded {len(profiles)} profiles: {list(profiles.keys())}")

# --- THE STATE DICT (single source of truth) ---
state = {
    # Global UI stuff
    "screen": screen,
    "font": font,
    "button_font": button_font,
    "button_color": button_color,
    "user_icon": USER_ICON,
    "add_icon": ADD_ICON,
    "profile_directory": PROFILE_DIRECTORY,

    # Global data
    "profiles": profiles,
    "profile_data": profile_data,

    # Routing
    "current_screen": "PROFILE_SELECT",

    # Input handling
    "last_click_time": 0,
    "click_cooldown": 250,

    # Per-screen state (gets reset by each screen's init())
    "selected_profile": None,
    "current_page": 0,
    "profile_layout": [],
    "adding_profile": False,
    "text_buffer": [""],
}

# --- Initialize the first screen ---
profile_select.init(state)

# --- Main loop ---
while running:
    mouse_pos = pygame.mouse.get_pos()
    clicked = False
    events = pygame.event.get()

    current_time = pygame.time.get_ticks()

    for event in events:
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if current_time - state["last_click_time"] > state["click_cooldown"]:
                    clicked = True
                    state["last_click_time"] = current_time

    screen.fill("#333333")

    # --- ROUTER ---
    if state["current_screen"] == "PROFILE_SELECT":
        profile_select.draw(state, mouse_pos, clicked, events)
    elif state["current_screen"] == "FEEDS":
        feed_screen.draw(state, mouse_pos, clicked, events)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
