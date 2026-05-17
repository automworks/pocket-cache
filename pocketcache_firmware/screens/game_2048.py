from __future__ import annotations

import random
import pygame

from .base import Screen
from ..theme import COLORS


class Game2048Screen(Screen):
    name = "game_2048"

    def __init__(self) -> None:
        self.grid = [[0] * 4 for _ in range(4)]
        self.score = 0
        self.message = "2048"
        self.game_over = False
        self.new_game()

    def new_game(self) -> None:
        self.grid = [[0] * 4 for _ in range(4)]
        self.score = 0
        self.message = "2048"
        self.game_over = False
        self._spawn()
        self._spawn()

    def _spawn(self) -> None:
        empty = [(r, c) for r in range(4) for c in range(4) if self.grid[r][c] == 0]
        if not empty:
            return
        r, c = random.choice(empty)
        self.grid[r][c] = 4 if random.random() < 0.1 else 2

    def _merge_line(self, line: list[int]) -> list[int]:
        nums = [n for n in line if n]
        out: list[int] = []
        skip = False
        for i, n in enumerate(nums):
            if skip:
                skip = False
                continue
            if i + 1 < len(nums) and nums[i + 1] == n:
                merged = n * 2
                self.score += merged
                out.append(merged)
                skip = True
            else:
                out.append(n)
        out += [0] * (4 - len(out))
        return out

    def _can_move(self) -> bool:
        if any(0 in row for row in self.grid):
            return True
        for r in range(4):
            for c in range(4):
                if c < 3 and self.grid[r][c] == self.grid[r][c + 1]:
                    return True
                if r < 3 and self.grid[r][c] == self.grid[r + 1][c]:
                    return True
        return False

    def _move(self, direction: str) -> None:
        if self.game_over:
            self.new_game()
            return

        before = [row[:] for row in self.grid]

        if direction == "left":
            self.grid = [self._merge_line(row) for row in self.grid]
        elif direction == "right":
            self.grid = [list(reversed(self._merge_line(list(reversed(row))))) for row in self.grid]
        elif direction == "up":
            cols = [[self.grid[r][c] for r in range(4)] for c in range(4)]
            merged = [self._merge_line(col) for col in cols]
            self.grid = [[merged[c][r] for c in range(4)] for r in range(4)]
        elif direction == "down":
            cols = [[self.grid[r][c] for r in range(4)] for c in range(4)]
            merged = [list(reversed(self._merge_line(list(reversed(col))))) for col in cols]
            self.grid = [[merged[c][r] for c in range(4)] for r in range(4)]

        if self.grid != before:
            self._spawn()
            self.message = "MOVE"
        else:
            self.message = "NO MOVE"

        if any(2048 in row for row in self.grid):
            self.message = "YOU WIN"
        elif not self._can_move():
            self.game_over = True
            self.message = "GAME OVER"

    def handle_game_action(self, action: str) -> str | None:
        # Four-button compromise:
        # A/left = move left
        # B/right = move right
        # Y/select = rotate through vertical move up/down
        # X/back = exit; hold/reopen via menu for reset.
        if action == "back":
            return "exit"
        if action == "left":
            self._move("left")
            return "handled"
        if action == "right":
            self._move("right")
            return "handled"
        if action == "select":
            # Alternate up/down using score parity-ish state for low-control hardware.
            # First select moves up, next select moves down.
            if not hasattr(self, "_vertical_toggle"):
                self._vertical_toggle = False
            self._vertical_toggle = not self._vertical_toggle
            self._move("up" if self._vertical_toggle else "down")
            return "handled"
        return None

    def draw(self, surf: pygame.Surface, ui, state) -> None:
        state.active_app = "game_2048"
        ui.header(surf, "2048", state.led_color)

        ui.text(surf, "2048", 16, 44, COLORS.text, ui.font_lg)
        ui.text(surf, f"SCORE {self.score}", 16, 82, COLORS.muted, ui.font_xs)
        ui.text(surf, self.message[:12], 134, 82, COLORS.accent, ui.font_xs)

        board_x = 16
        board_y = 112
        cell = 50
        gap = 4

        pygame.draw.rect(surf, COLORS.panel, (board_x - 4, board_y - 4, 4 * cell + 5 * gap, 4 * cell + 5 * gap), border_radius=8)

        for r in range(4):
            for c in range(4):
                value = self.grid[r][c]
                x = board_x + c * (cell + gap)
                y = board_y + r * (cell + gap)

                bg = (28, 34, 38)
                if value:
                    # Deliberately uses existing palette, not many colors.
                    bg = (38 + min(120, value.bit_length() * 8), 48, 54)

                pygame.draw.rect(surf, bg, (x, y, cell, cell), border_radius=6)
                if value:
                    font = ui.font_md if value < 1000 else ui.font
                    rendered = font.render(str(value), True, COLORS.text)
                    surf.blit(rendered, (x + (cell - rendered.get_width()) // 2, y + (cell - rendered.get_height()) // 2))

        ui.footer(surf, "X EXIT  Y UP/DN  A LEFT  B RIGHT")
