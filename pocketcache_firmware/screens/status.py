from __future__ import annotations

import math
import pygame

from .base import Screen
from ..theme import COLORS
from ..state import format_uptime


class StatusScreen(Screen):
    name = "status"

    def _bar(self, surf, ui, label, value, x, y, color):
        ui.text(surf, label, x, y, COLORS.muted, ui.font_xs)
        ui.text(surf, f"{int(value)}%", x + 126, y, COLORS.text, ui.font_xs)
        ui.progress_bar(surf, x, y + 19, 200, 12, int(value), color)

    def draw(self, surf: pygame.Surface, ui, state) -> None:
        state.active_app = "status"
        ui.header(surf, "BACK", led=state.led_color)

        battery_color = COLORS.bad if state.battery_pct <= 15 else COLORS.warn if state.battery_pct <= 30 else COLORS.ok

        ui.text(surf, "DEVICE", 16, 46, COLORS.text, ui.font_md)
        ui.text(surf, f"UP {format_uptime(state.uptime_seconds)}", 16, 76, COLORS.muted, ui.font_xs)
        ui.text(surf, f"IP {state.ip_address}", 118, 76, COLORS.muted, ui.font_xs)

        self._bar(surf, ui, "BATTERY", state.battery_pct, 16, 106, battery_color)
        self._bar(surf, ui, "CPU LOAD", state.cpu_load_pct, 16, 142, COLORS.accent)
        self._bar(surf, ui, "MEMORY", state.memory_pct, 16, 178, COLORS.warn)
        self._bar(surf, ui, "WIFI", state.wifi_signal_pct, 16, 214, COLORS.ok)

        ui.text(surf, f"TEMP {state.cpu_temp_c:.1f}C", 16, 248, COLORS.text, ui.font_xs)
        ui.text(surf, f"CLIENTS {state.clients}", 126, 248, COLORS.text, ui.font_xs)
        ui.text(surf, f"SERVED {state.packets_served}", 16, 265, COLORS.muted, ui.font_xs)

        ui.footer(surf, "MENU", "MENU")
