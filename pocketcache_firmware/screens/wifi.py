from __future__ import annotations

import pygame

from .base import Screen
from ..theme import COLORS, WIDTH
from ..qr import make_qr_surface


class WifiScreen(Screen):
    name = "wifi"

    def draw(self, surf: pygame.Surface, ui, state) -> None:
        state.active_app = "portal"
        ui.header(surf, "join wifi", state.led_color)
        payload = f"WIFI:T:WPA;S:{state.ssid};P:{state.password};;"
        qr = make_qr_surface(payload, 166)
        surf.blit(qr, ((WIDTH - 166) // 2, 48))

        ui.centered_text(surf, "SSID", 222, COLORS.muted, ui.font_xs)
        ui.centered_text(surf, state.ssid, 241, COLORS.text, ui.font_md)
        ui.centered_text(surf, "PASS  " + state.password, 271, COLORS.accent, ui.font_sm)

        ui.footer(surf, "X BACK  Y SELECT  A LEFT  B RIGHT")
