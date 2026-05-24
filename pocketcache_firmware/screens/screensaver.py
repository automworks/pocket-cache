from __future__ import annotations

import pygame

from .base import Screen


class ScreensaverScreen(Screen):
    name = "screensaver"

    def draw(self, surf: pygame.Surface, ui, state) -> None:
        state.active_app = "screensaver"
        surf.fill((0, 0, 0))
