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

HEADER_H = 40
FOOTER_H = 40
BODY_Y = HEADER_H + 6
BODY_H = HEIGHT - HEADER_H - FOOTER_H - 12
FOOTER_Y = HEIGHT - FOOTER_H
PADDING = 8
