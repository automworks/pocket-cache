from __future__ import annotations

import string
import pygame

from .base import Screen
from ..theme import COLORS
from ..config_manager import (
    PocketCacheConfig,
    apply_runtime_config_to_state,
    load_config,
    save_config,
    write_hostapd_config,
    restart_network_services,
    reboot_pi,
)


CHARS = " " + string.ascii_letters + string.digits + "-_."


class SettingsScreen(Screen):
    name = "settings"

    def __init__(self) -> None:
        self.config = load_config()
        self.rows = [
            ("SSID", "ssid"),
            ("PASS", "password"),
            ("LED", "led"),
            ("SAVE WIFI", "save"),
            ("RESTART PI", "reboot"),
        ]
        self.row = 0
        self.cursor = 0
        self.editing = False
        self.message = "Y SELECT"

    def _current_value(self) -> str:
        key = self.rows[self.row][1]
        if key == "ssid":
            return self.config.ssid
        if key == "password":
            return self.config.password
        return ""

    def _set_current_value(self, value: str) -> None:
        key = self.rows[self.row][1]
        if key == "ssid":
            self.config.ssid = value[:24]
        elif key == "password":
            self.config.password = value[:32]

    def _cycle_char(self, delta: int) -> None:
        value = self._current_value()
        if not value:
            value = " "
        self.cursor = max(0, min(self.cursor, len(value) - 1))
        current = value[self.cursor]
        idx = CHARS.find(current)
        if idx < 0:
            idx = 0
        new = CHARS[(idx + delta) % len(CHARS)]
        value = value[:self.cursor] + new + value[self.cursor + 1:]
        self._set_current_value(value)

    def _move_row(self, delta: int) -> None:
        self.row = (self.row + delta) % len(self.rows)
        self.cursor = min(self.cursor, max(0, len(self._current_value()) - 1))
        self.editing = False
        self.message = self.rows[self.row][0]

    def _select(self, state) -> None:
        label, key = self.rows[self.row]

        if key in ("ssid", "password"):
            if not self.editing:
                self.editing = True
                self.cursor = min(self.cursor, max(0, len(self._current_value()) - 1))
                self.message = f"EDIT {label}"
            else:
                value = self._current_value()
                insert_at = min(self.cursor + 1, len(value))
                value = value[:insert_at] + " " + value[insert_at:]
                self._set_current_value(value)
                self.cursor = insert_at
                self.message = "ADD CHAR"
            return

        if key == "led":
            self.config.led_enabled = not self.config.led_enabled
            state.led_enabled = self.config.led_enabled
            self.message = "LED ON" if self.config.led_enabled else "LED OFF"
            return

        if key == "save":
            try:
                save_config(self.config)
                apply_runtime_config_to_state(state, self.config)
                write_hostapd_config(self.config)
                restart_network_services()
                self.message = "WIFI SAVED"
            except PermissionError:
                # Allows simulator testing without sudo.
                save_config(self.config, load_config.__globals__["DEFAULT_CONFIG_PATH"].expanduser())
                apply_runtime_config_to_state(state, self.config)
                self.message = "SAVED CONFIG"
            except Exception as exc:
                self.message = f"ERR {type(exc).__name__}"[:14]
            return

        if key == "reboot":
            self.message = "REBOOTING"
            reboot_pi()

    def handle_settings_action(self, action: str, state) -> str | None:
        if action == "back":
            if self.editing:
                # Backspace while editing; exit if field is empty.
                value = self._current_value()
                if value and self.cursor < len(value):
                    value = value[:self.cursor] + value[self.cursor + 1:]
                    self._set_current_value(value)
                    self.cursor = max(0, min(self.cursor, len(value) - 1))
                    self.message = "DELETE"
                    return "handled"
                self.editing = False
                return "handled"
            return "exit"

        if action == "left":
            if self.editing:
                if self.cursor > 0:
                    self.cursor -= 1
                else:
                    self._cycle_char(-1)
            else:
                self._move_row(-1)
            return "handled"

        if action == "right":
            if self.editing:
                value = self._current_value()
                if self.cursor < len(value) - 1:
                    self.cursor += 1
                else:
                    self._cycle_char(1)
            else:
                self._move_row(1)
            return "handled"

        if action == "select":
            self._select(state)
            return "handled"

        return None

    def draw(self, surf: pygame.Surface, ui, state) -> None:
        state.active_app = "settings"
        ui.header(surf, "settings", state.led_color)

        ui.centered_text(surf, "DEVICE", 42, COLORS.text, ui.font_md)
        ui.centered_text(surf, "SETTINGS", 66, COLORS.accent, ui.font_md)

        y = 108
        for idx, (label, key) in enumerate(self.rows):
            selected = idx == self.row
            bg = (48, 42, 36) if selected else COLORS.panel
            pygame.draw.rect(surf, bg, (12, y, 216, 34), border_radius=7)
            if selected:
                pygame.draw.rect(surf, COLORS.warn, (12, y, 5, 34), border_radius=3)

            ui.text(surf, label, 22, y + 8, COLORS.text if selected else COLORS.muted, ui.font_xs)

            if key in ("ssid", "password"):
                raw = self._current_value()
                value = raw if key == "ssid" else "*" * len(raw)
                shown = value[:13]
                ui.text(surf, shown, 100, y + 8, COLORS.text, ui.font_xs)

                if selected and self.editing:
                    cx = 100 + min(self.cursor, 12) * 9
                    pygame.draw.rect(surf, COLORS.accent, (cx, y + 27, 8, 3))
            elif key == "led":
                value = "ON" if self.config.led_enabled else "OFF"
                ui.text(surf, value, 150, y + 8, COLORS.ok if self.config.led_enabled else COLORS.muted, ui.font_xs)
            y += 40

        mode = "EDIT" if self.editing else "NAV"
        ui.centered_text(surf, f"{mode} • {self.message}", 278, COLORS.muted, ui.font_xs)

        if self.editing:
            ui.footer(surf, "X DEL  Y ADD  A/B MOVE")
        else:
            ui.footer(surf, "X BACK  Y SELECT  A/B ROW")
