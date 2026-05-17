from __future__ import annotations

import pygame

from ..state import DeviceState


class Screen:
    name = "screen"

    def draw(self, surf: pygame.Surface, ui, state: DeviceState) -> None:
        raise NotImplementedError
