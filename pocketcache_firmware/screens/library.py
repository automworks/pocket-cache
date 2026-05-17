from __future__ import annotations

import pygame

from .base import Screen
from ..theme import COLORS


class LibraryScreen(Screen):
    name = "library"

    def draw(self, surf: pygame.Surface, ui, state) -> None:
        state.active_app = "library"
        ui.header(surf, "BACK", led=state.led_color)
        ui.text(surf, "CONTENT", 16, 48, COLORS.text, ui.font_md)

        items = list(state.content.items())
        y = 84
        for label, ok in items:
            ui.status_chip(surf, label, ok, 16, y, 208)
            y += 31

        ui.divider(surf, 264)
        ui.text(surf, "KIWIX", 16, 270, COLORS.muted, ui.font_xs)
        ui.status_chip(surf, "kiwix", state.services["kiwix"], 82, 266, 104)

        ui.footer(surf)
