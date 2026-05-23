from dataclasses import dataclass

# Portrait firmware canvas. The Display HAT adapter rotates this 240x320 canvas
# onto the physical 320x240 LCD framebuffer.
WIDTH = 240
HEIGHT = 320

PHYSICAL_WIDTH = 320
PHYSICAL_HEIGHT = 240


@dataclass(frozen=True)
class Colors:
    bg: tuple[int, int, int] = (0, 0, 0)
    panel: tuple[int, int, int] = (17, 17, 17)
    chrome: tuple[int, int, int] = (34, 34, 34)
    text: tuple[int, int, int] = (255, 255, 255)
    muted: tuple[int, int, int] = (164, 174, 172)
    ok: tuple[int, int, int] = (71, 220, 125)
    warn: tuple[int, int, int] = (245, 190, 75)
    bad: tuple[int, int, int] = (245, 90, 90)
    accent: tuple[int, int, int] = (112, 220, 255)
    hi: tuple[int, int, int] = (255, 115, 0)
    qr_bg: tuple[int, int, int] = (240, 240, 232)
    qr_fg: tuple[int, int, int] = (0, 0, 0)


COLORS = Colors()

# App-specific accent colors (Figma design system)
APP_COLORS = {
    "menu": (255, 115, 0),        # FF7300 - orange
    "library": (0, 207, 107),      # 00CF6B - green
    "games": (255, 0, 183),        # FF00B7 - magenta
    "connect": (255, 115, 0),      # FF7300 - orange
    "settings": (0, 60, 255),      # 003CFF - blue
    "reader": (138, 56, 245),      # 8A38F5 - purple
    "status": (0, 60, 255),        # 003CFF - blue
    "about": (138, 56, 245),       # 8A38F5 - purple
    "sudoku": (255, 115, 0),       # FF7300 - orange (games)
    "game_2048": (255, 0, 183),    # FF00B7 - magenta (games)
    "game_mines": (255, 0, 183),   # FF00B7 - magenta (games)
    "game_blackjack": (255, 0, 183),  # FF00B7 - magenta (games)
    "game_chess": (255, 0, 183),   # FF00B7 - magenta (games)
    "game_tetris": (255, 0, 183),  # FF00B7 - magenta (games)
    "game_life": (255, 0, 183),    # FF00B7 - magenta (games)
    "game_dice": (255, 0, 183),    # FF00B7 - magenta (games)
    "games_menu": (255, 0, 183),   # FF00B7 - magenta (games)
    "alert": (255, 0, 183),        # FF00B7 - magenta (warning)
    "boot": (112, 220, 255),       # Cyan (system)
}

HEADER_H = 40
FOOTER_H = 40
BODY_Y = HEADER_H + 6
BODY_H = HEIGHT - HEADER_H - FOOTER_H - 12
FOOTER_Y = HEIGHT - FOOTER_H
PADDING = 8
