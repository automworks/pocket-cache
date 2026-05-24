from __future__ import annotations

import os
import pygame

from .base import Screen
from ..theme import COLORS, WIDTH
from ..qr import make_qr_surface


class PortalScreen(Screen):
    name = "connect"

    def __init__(self) -> None:
        self.modes = ["hello", "portal", "wifi"]
        self.dev_mode = os.environ.get("POCKETCACHE_DEV") == "1"
        self.index = 2 if self.dev_mode else 0

    @property
    def mode(self) -> str:
        return self.modes[self.index]

    def handle_portal_action(self, action: str) -> str | None:
        if action == "back":
            return "reboot" if self.dev_mode else "exit"
        if action == "left":
            self.index = (self.index - 1) % len(self.modes)
            return "handled"
        if action == "right" or action == "select":
            self.index = (self.index + 1) % len(self.modes)
            return "handled"
        return None

    def draw(self, surf: pygame.Surface, ui, state) -> None:
        state.active_app = "connect"
        back_label = "REBOOT" if self.dev_mode else "BACK"
        ui.header(surf, back_label, "MODE", state.led_color)
        if self.dev_mode:
            ui.text(surf, "DEV", WIDTH - 38, 12, COLORS.warn, ui.font_xs)

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
