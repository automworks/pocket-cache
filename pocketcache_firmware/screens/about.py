from __future__ import annotations

import pygame

from .base import Screen
from ..theme import COLORS


class AboutScreen(Screen):
    name = "about"

    def draw(self, surf: pygame.Surface, ui, state) -> None:
        state.active_app = "about"
        ui.header(surf, "BACK", led=state.led_color)
        accent = state.app_accent_color
        ui.centered_text(surf, "POCKET", 52, COLORS.text, ui.font_lg)
        ui.centered_text(surf, "CACHE", 86, accent, ui.font_lg)
        ui.centered_text(surf, "PRIVATE STASH", 130, COLORS.muted, ui.font_sm)
        ui.centered_text(surf, "OF KNOWLEDGE", 152, COLORS.muted, ui.font_sm)

        lines = [
            "LOCAL HOTSPOT",
            "OFFLINE LIBRARY",
            "MAPS + REPAIR",
            "BOOKS + GAMES",
        ]
        y = 186
        for line in lines:
            ui.centered_text(surf, line, y, COLORS.text, ui.font)
            y += 22

        ui.footer(surf, "PREV", "NEXT")
