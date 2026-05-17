from __future__ import annotations

import math
import pygame

from .base import Screen
from ..theme import COLORS, PADDING


class AppMenuScreen(Screen):
    name = "menu"

    def __init__(self) -> None:
        # Keep launcher labels short. No descriptions: the 240x320 LCD overflows quickly.
        self.items = [
            ("Library", "library"),
            ("Play", "games"),
            ("Connect", "portal"),
            ("Status", "status"),
            ("Settings", "settings"),
            ("About", "about"),
        ]
        self.index = 0
        self.page_size = 4

    @property
    def page_count(self) -> int:
        return max(1, math.ceil(len(self.items) / self.page_size))

    @property
    def page(self) -> int:
        return self.index // self.page_size

    def handle_menu_action(self, action: str) -> str | None:
        if action == "left":
            self.index = (self.index - 1) % len(self.items)
            return "handled"
        if action == "right":
            self.index = (self.index + 1) % len(self.items)
            return "handled"
        if action == "select":
            return self.items[self.index][1]
        if action == "back":
            return "handled"
        return None

    def draw(self, surf: pygame.Surface, ui, state) -> None:
        state.active_app = "menu"
        ui.header(surf, "EXIT", "OPEN", state.led_color)

        #ui.centered_text(surf, "POCKET", 42, COLORS.text, ui.font_lg)
        #ui.centered_text(surf, "CACHE", 76, COLORS.accent, ui.font_lg)
        #ui.centered_text(surf, f"PAGE {self.page + 1}/{self.page_count}", 112, COLORS.muted, ui.font_xs)

        start = self.page * self.page_size
        visible = self.items[start:start + self.page_size]

        y = 50
        for offset, (title, app_id) in enumerate(visible):
            i = start + offset
            selected = i == self.index
            x = 18
            w = 204
            h = 40
            fg = COLORS.text if selected else COLORS.muted

            pygame.draw.rect(surf, COLORS.panel, (x, y, w, h), border_radius=8)
            if selected:
                pygame.draw.rect(surf, COLORS.hi, (x, y, w, h), 2, border_radius=8)
                plus = ui.font.render("+", True, COLORS.hi)
                surf.blit(plus, (x + w - PADDING - plus.get_width(), y + (h - plus.get_height()) // 2))

            ui.centered_text(surf, title.upper(), y + 8, fg, ui.font)
            y += 50

        # Page dots
        dot_y = 278
        total_w = self.page_count * 14
        dot_x = (240 - total_w) // 2
        for p in range(self.page_count):
            color = COLORS.accent if p == self.page else COLORS.muted
            pygame.draw.circle(surf, color, (dot_x + p * 14, dot_y), 4)

        ui.footer(surf, "PREV", "NEXT")
