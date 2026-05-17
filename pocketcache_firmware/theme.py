from dataclasses import dataclass

# Portrait firmware canvas. The Display HAT adapter rotates this 240x320 canvas
# onto the physical 320x240 LCD framebuffer.
WIDTH = 240
HEIGHT = 320

PHYSICAL_WIDTH = 320
PHYSICAL_HEIGHT = 240


@dataclass(frozen=True)
class Colors:
    bg: tuple[int, int, int] = (8, 10, 12)
    panel: tuple[int, int, int] = (18, 22, 25)
    text: tuple[int, int, int] = (238, 241, 235)
    muted: tuple[int, int, int] = (164, 174, 172)
    ok: tuple[int, int, int] = (71, 220, 125)
    warn: tuple[int, int, int] = (245, 190, 75)
    bad: tuple[int, int, int] = (245, 90, 90)
    accent: tuple[int, int, int] = (112, 220, 255)
    hi: tuple[int, int, int] = (255, 128, 0)
    qr_bg: tuple[int, int, int] = (240, 240, 232)
    qr_fg: tuple[int, int, int] = (8, 10, 12)


COLORS = Colors()

HEADER_H = 34
FOOTER_H = 34
BODY_Y = HEADER_H + 6
BODY_H = HEIGHT - HEADER_H - FOOTER_H - 12
FOOTER_Y = HEIGHT - FOOTER_H
PADDING = 8
