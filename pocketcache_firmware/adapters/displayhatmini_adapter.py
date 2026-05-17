from __future__ import annotations

import colorsys
import os
import signal
import time
from time import monotonic

import pygame
from displayhatmini import DisplayHATMini

from ..theme import WIDTH, HEIGHT, PHYSICAL_WIDTH, PHYSICAL_HEIGHT, COLORS


class DisplayHatMiniAdapter:
    """Portrait renderer for Pimoroni Display HAT Mini.

    The app draws to a 240x320 portrait canvas, then rotates that surface to the
    physical 320x240 LCD framebuffer.

    Orientation can be changed without code edits:

        POCKETCACHE_ROTATION=cw   python -m pocketcache_firmware.displayhat_main
        POCKETCACHE_ROTATION=ccw  python -m pocketcache_firmware.displayhat_main
        POCKETCACHE_ROTATION=180  python -m pocketcache_firmware.displayhat_main

    Default is 180.
    """

    def __init__(self, fps: int = 20) -> None:
        os.environ["SDL_VIDEODRIVER"] = "dummy"

        self.display_hat = DisplayHATMini(None)
        self.width = self.display_hat.WIDTH
        self.height = self.display_hat.HEIGHT
        if self.width != PHYSICAL_WIDTH or self.height != PHYSICAL_HEIGHT:
            raise RuntimeError(f"Expected physical {PHYSICAL_WIDTH}x{PHYSICAL_HEIGHT}, got {self.width}x{self.height}")

        pygame.display.init()
        pygame.font.init()

        self.logical = pygame.Surface((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True
        self.target_fps = fps
        self.rotation = os.environ.get("POCKETCACHE_ROTATION", "180").lower()
        self._last_led: tuple[int, int, int] | None = None

        # Physical portrait layout:
        # Top row, left to right: X, Y
        # Bottom row, left to right: A, B
        #
        # Firmware actions:
        # X = Back
        # Y = Select
        # A = Left / previous
        # B = Right / next
        self._button_map = {
            self.display_hat.BUTTON_X: "back",
            self.display_hat.BUTTON_Y: "select",
            self.display_hat.BUTTON_A: "left",
            self.display_hat.BUTTON_B: "right",
        }
        self._button_was_down = {pin: False for pin in self._button_map}
        self._last_press_at = {pin: 0.0 for pin in self._button_map}
        self._debounce_seconds = 0.18

        signal.signal(signal.SIGINT, self._exit)
        signal.signal(signal.SIGTERM, self._exit)

        self.clear()
        self.rainbow_boot_animation()
        self.present()


    def rainbow_boot_animation(self, duration: float = 2.4, fps: int = 30) -> None:
        """Cycle the Display HAT Mini RGB LED through a rainbow during boot."""

        frames = max(1, int(duration * fps))
        for i in range(frames):
            hue = (i / frames) % 1.0
            r, g, b = colorsys.hsv_to_rgb(hue, 1.0, 1.0)
            self.display_hat.set_led(r, g, b)
            time.sleep(1 / fps)

        self.display_hat.set_led(1.0, 1.0, 1.0)
        time.sleep(0.12)
        self.display_hat.set_led(0.0, 0.0, 0.0)
        self._last_led = None

    def _exit(self, sig, frame) -> None:
        self.running = False

    def clear(self) -> None:
        self.logical.fill(COLORS.bg)

    def _rotate_for_display(self) -> pygame.Surface:
        if self.rotation in ("cw", "90", "right"):
            return pygame.transform.rotate(self.logical, -90)
        if self.rotation in ("ccw", "270", "left"):
            return pygame.transform.rotate(self.logical, 90)
        if self.rotation in ("180", "flip", "inverted"):
            # For a physically portrait-mounted display that needs a vertical flip,
            # rotate to landscape, then invert.
            return pygame.transform.rotate(pygame.transform.rotate(self.logical, -90), 180)
        return pygame.transform.rotate(self.logical, -90)

    def present(self) -> None:
        self.display_hat.st7789.set_window()

        framebuffer = self._rotate_for_display()
        if framebuffer.get_size() != (PHYSICAL_WIDTH, PHYSICAL_HEIGHT):
            framebuffer = pygame.transform.scale(framebuffer, (PHYSICAL_WIDTH, PHYSICAL_HEIGHT))

        pixelbytes = framebuffer.convert(16, 0).get_buffer()
        pixelbytes = bytearray(pixelbytes)
        pixelbytes[0::2], pixelbytes[1::2] = pixelbytes[1::2], pixelbytes[0::2]

        for i in range(0, len(pixelbytes), 4096):
            self.display_hat.st7789.data(pixelbytes[i:i + 4096])

    def poll(self) -> list[str]:
        actions: list[str] = []

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                actions.append("quit")

        now = monotonic()

        for pin, action in self._button_map.items():
            is_down = bool(self.display_hat.read_button(pin))
            was_down = self._button_was_down[pin]

            if is_down and not was_down and now - self._last_press_at[pin] >= self._debounce_seconds:
                actions.append(action)
                self._last_press_at[pin] = now

            self._button_was_down[pin] = is_down

        return actions

    def set_led(self, rgb: tuple[int, int, int]) -> None:
        if rgb == self._last_led:
            return

        r, g, b = rgb
        self.display_hat.set_led(r / 255.0, g / 255.0, b / 255.0)
        self._last_led = rgb

    def fps(self, value: int | None = None) -> None:
        self.clock.tick(value or self.target_fps)

    def close(self) -> None:
        try:
            self.display_hat.set_led(0, 0, 0)
        except Exception:
            pass
        pygame.quit()
