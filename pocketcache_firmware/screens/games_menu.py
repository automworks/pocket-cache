from __future__ import annotations

import math
import pygame

from .base import Screen
from ..theme import COLORS


class GamesMenuScreen(Screen):
    name = "games_menu"

    def __init__(self) -> None:
        self.items = [
            ("Sudoku", "sudoku"),
            ("2048", "game_2048"),
            ("Mines", "game_mines"),
            ("Blackjack", "blackjack"),
            ("Chess", "chess"),
            ("Tetris", "tetris"),
            ("Life", "life"),
            ("D20 Dice", "dice"),
        ]
        self.index = 0
        self.page_size = 4
        self.message = "SELECT GAME"

    @property
    def page_count(self) -> int:
        return max(1, math.ceil(len(self.items) / self.page_size))

    @property
    def page(self) -> int:
        return self.index // self.page_size

    def handle_games_menu_action(self, action: str) -> str | None:
        if action == "back":
            return "exit"
        if action == "left":
            self.index = (self.index - 1) % len(self.items)
            self.message = "SELECT GAME"
            return "handled"
        if action == "right":
            self.index = (self.index + 1) % len(self.items)
            self.message = "SELECT GAME"
            return "handled"
        if action == "select":
            return self.items[self.index][1]
        return None

    def draw(self, surf: pygame.Surface, ui, state) -> None:
        state.active_app = "games"
        ui.header(surf, "BACK", "OPEN", state.led_color)

        start = self.page * self.page_size
        visible = self.items[start:start + self.page_size]

        y = 50
        for offset, (title, app_id) in enumerate(visible):
            i = start + offset
            selected = i == self.index
            x = 18
            w = 204
            h = 40
            fg = COLORS.text if selected else COLORS.muted

            pygame.draw.rect(surf, COLORS.panel, (x, y, w, h), border_radius=8)
            if selected:
                pygame.draw.rect(surf, COLORS.hi, (x, y, w, h), 2, border_radius=8)

            ui.centered_text(surf, title.upper(), y + 8, fg, ui.font)
            y += 50

        # Page dots
        dot_y = 278
        total_w = self.page_count * 14
        dot_x = (240 - total_w) // 2
        for p in range(self.page_count):
            color = COLORS.accent if p == self.page else COLORS.muted
            pygame.draw.circle(surf, color, (dot_x + p * 14, dot_y), 4)

        ui.footer(surf, "PREV", "NEXT")
