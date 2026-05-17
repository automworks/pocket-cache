from __future__ import annotations

import pygame

from .base import Screen
from ..theme import COLORS


class AlertScreen(Screen):
    name = "alert"

    def draw(self, surf: pygame.Surface, ui, state) -> None:
        ui.header(surf, "alert", state.led_color)
        ui.centered_text(surf, "ALERT", 52, COLORS.bad, ui.font_lg)

        y = 104
        if state.battery_pct <= 15:
            ui.centered_text(surf, f"LOW BATTERY", y, COLORS.bad, ui.font_md)
            y += 28
            ui.centered_text(surf, f"{state.battery_pct}%", y, COLORS.text, ui.font_md)
            y += 36

        bad_services = [k.upper() for k, v in state.services.items() if not v]
        if bad_services:
            ui.centered_text(surf, "SERVICE DOWN", y, COLORS.bad, ui.font_md)
            y += 28
            ui.centered_text(surf, ", ".join(bad_services), y, COLORS.text, ui.font)
            y += 36

        bad_content = [k.upper() for k, v in state.content.items() if not v]
        if bad_content:
            ui.centered_text(surf, "CONTENT MISSING", y, COLORS.warn, ui.font_md)
            y += 28
            ui.centered_text(surf, ", ".join(bad_content), y, COLORS.text, ui.font)

        if not state.has_alert:
            ui.centered_text(surf, "ALL SYSTEMS", 132, COLORS.ok, ui.font_md)
            ui.centered_text(surf, "NOMINAL", 162, COLORS.ok, ui.font_md)

        ui.footer(surf, "X BACK  Y ACK")
