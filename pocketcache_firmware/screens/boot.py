from __future__ import annotations

import math
from time import monotonic
import pygame

from .base import Screen
from ..theme import COLORS, WIDTH
from ..state import DeviceState


class BootScreen(Screen):
    name = "boot"

    def draw(self, surf: pygame.Surface, ui, state: DeviceState) -> None:
        state.active_app = "boot"
        ui.header(surf, back=None, led=state.led_color)

        elapsed = monotonic() - state.boot_started_at
        progress = max(0.0, min(1.0, elapsed / 3.5))

        ui.centered_text(surf, "BOOT", 44, COLORS.text, ui.font_lg)
        ui.centered_text(surf, "POCKET-CACHE", 82, COLORS.accent, ui.font_md)

        # Spinner ring
        cx, cy = WIDTH // 2, 142
        radius = 28
        for i in range(12):
            angle = elapsed * 6 + i * (math.tau / 12)
            alpha_rank = (i + int(elapsed * 12)) % 12
            color = COLORS.accent if alpha_rank > 7 else COLORS.muted
            x = int(cx + math.cos(angle) * radius)
            y = int(cy + math.sin(angle) * radius)
            pygame.draw.circle(surf, color, (x, y), 3)

        # Progress bar
        ui.progress_bar(surf, 28, 186, 184, 14, int(progress * 100), COLORS.accent)

        steps = [
            ("HOTSPOT", elapsed > 0.5),
            ("PORTAL", elapsed > 1.2),
            ("LIBRARY", elapsed > 2.0),
            ("READY", elapsed > 3.0),
        ]
        y = 212
        for label, ok in steps:
            marker = "OK" if ok else "--"
            color = COLORS.ok if ok else COLORS.muted
            ui.text(surf, f"{marker} {label}", 38, y, color, ui.font_xs)
            y += 16

        ui.footer(surf)
