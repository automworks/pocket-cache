from __future__ import annotations

import pygame

from .base import Screen
from ..theme import COLORS, WIDTH
from ..qr import make_qr_surface


class PortalScreen(Screen):
    name = "portal"

    def __init__(self) -> None:
        self.modes = ["hello", "portal", "wifi"]
        self.index = 0

    @property
    def mode(self) -> str:
        return self.modes[self.index]

    def handle_portal_action(self, action: str) -> str | None:
        if action == "back":
            return "exit"
        if action == "left":
            self.index = (self.index - 1) % len(self.modes)
            return "handled"
        if action == "right" or action == "select":
            self.index = (self.index + 1) % len(self.modes)
            return "handled"
        return None

    def draw(self, surf: pygame.Surface, ui, state) -> None:
        state.active_app = "portal"
        ui.header(surf, "BACK", "MODE", state.led_color)

        if self.mode == "wifi":
            payload = f"WIFI:T:WPA;S:{state.ssid};P:{state.password};;"
            label = "JOIN WIFI"
            detail_1 = state.ssid[:18]
            detail_2 = "SCAN TO JOIN"
        elif self.mode == "portal":
            payload = state.portal_url
            label = "PORTAL"
            detail_1 = "10.0.0.1"
            detail_2 = "HOME PAGE"
        else:
            payload = f"{state.portal_url}/hello.html"
            label = "HELLO TEST"
            detail_1 = "10.0.0.1/HELLO"
            detail_2 = "WEB SERVER TEST"

        accent = state.app_accent_color
        qr = make_qr_surface(payload, 168)
        surf.blit(qr, ((WIDTH - 168) // 2, 44))

        ui.centered_text(surf, label, 222, accent, ui.font_sm)
        ui.centered_text(surf, detail_1, 246, COLORS.text, ui.font_xs)
        ui.centered_text(surf, detail_2, 268, COLORS.muted, ui.font_xs)

        # Small mode dots
        dot_x = (WIDTH - 42) // 2
        for i in range(3):
            pygame.draw.circle(surf, accent if i == self.index else COLORS.muted, (dot_x + i * 21, 262), 4)

        ui.footer(surf, "QR", "QR")
