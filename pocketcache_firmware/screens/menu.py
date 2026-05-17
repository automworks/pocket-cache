from __future__ import annotations

import math
import pygame

from .base import Screen
from ..theme import COLORS


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

        ui.text(surf, "/MENU", 16, 52, COLORS.muted, ui.font_xs)

        start = self.page * self.page_size
        visible = self.items[start:start + self.page_size]

        y = 78
        for offset, (title, app_id) in enumerate(visible):
            i = start + offset
            selected = i == self.index
            x = 16
            w = 208
            h = 48
            item_bg = COLORS.chrome if selected else COLORS.panel
            fg = COLORS.text if selected else COLORS.muted

            pygame.draw.rect(surf, item_bg, (x, y, w, h), border_radius=8)
            if selected:
                pygame.draw.rect(surf, COLORS.hi, (x, y, w, h), 2, border_radius=8)
                plus = ui.font.render("+", True, COLORS.hi)
                surf.blit(plus, (x + w - 14 - plus.get_width(), y + (h - plus.get_height()) // 2))
                ui.text(surf, title.upper(), x + 14, y + (h - ui.font.get_height()) // 2, fg, ui.font)
            else:
                ui.text(surf, title.upper(), x + 16, y + (h - ui.font.get_height()) // 2, fg, ui.font)

            y += 56

        # Page dots (8×8 squares)
        dot_y = 255
        dot_size = 8
        gap = 10
        total_w = self.page_count * (dot_size + gap) - gap
        dot_x = (240 - total_w) // 2
        for p in range(self.page_count):
            color = COLORS.accent if p == self.page else COLORS.muted
            pygame.draw.rect(surf, color, (dot_x + p * (dot_size + gap), dot_y, dot_size, dot_size), border_radius=2)

        ui.footer(surf, "PREV", "NEXT")
