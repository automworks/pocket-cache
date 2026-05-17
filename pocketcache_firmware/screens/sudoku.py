from __future__ import annotations

import pygame

from .base import Screen
from ..theme import COLORS, WIDTH


PUZZLE = [
    [5, 3, 0, 0, 7, 0, 0, 0, 0],
    [6, 0, 0, 1, 9, 5, 0, 0, 0],
    [0, 9, 8, 0, 0, 0, 0, 6, 0],
    [8, 0, 0, 0, 6, 0, 0, 0, 3],
    [4, 0, 0, 8, 0, 3, 0, 0, 1],
    [7, 0, 0, 0, 2, 0, 0, 0, 6],
    [0, 6, 0, 0, 0, 0, 2, 8, 0],
    [0, 0, 0, 4, 1, 9, 0, 0, 5],
    [0, 0, 0, 0, 8, 0, 0, 7, 9],
]

SOLUTION = [
    [5, 3, 4, 6, 7, 8, 9, 1, 2],
    [6, 7, 2, 1, 9, 5, 3, 4, 8],
    [1, 9, 8, 3, 4, 2, 5, 6, 7],
    [8, 5, 9, 7, 6, 1, 4, 2, 3],
    [4, 2, 6, 8, 5, 3, 7, 9, 1],
    [7, 1, 3, 9, 2, 4, 8, 5, 6],
    [9, 6, 1, 5, 3, 7, 2, 8, 4],
    [2, 8, 7, 4, 1, 9, 6, 3, 5],
    [3, 4, 5, 2, 8, 6, 1, 7, 9],
]


class SudokuScreen(Screen):
    name = "sudoku"

    def __init__(self) -> None:
        self.grid = [row[:] for row in PUZZLE]
        self.cursor = self._first_editable()
        self.pick = 1
        self.mistakes = 0
        self.message = "A CELL  B NUM  X SET"

    def _first_editable(self) -> tuple[int, int]:
        for r in range(9):
            for c in range(9):
                if PUZZLE[r][c] == 0:
                    return r, c
        return 0, 0

    def _editable_cells(self) -> list[tuple[int, int]]:
        return [(r, c) for r in range(9) for c in range(9) if PUZZLE[r][c] == 0]

    def move_cursor(self) -> None:
        cells = self._editable_cells()
        idx = cells.index(self.cursor) if self.cursor in cells else 0
        self.cursor = cells[(idx + 1) % len(cells)]
        r, c = self.cursor
        self.pick = self.grid[r][c] or self.pick or 1
        self.message = "CELL"

    def cycle_number(self) -> None:
        self.pick = (self.pick % 9) + 1
        self.message = f"NUMBER {self.pick}"

    def set_number(self) -> None:
        r, c = self.cursor
        if PUZZLE[r][c] != 0:
            self.message = "LOCKED"
            return

        if self.grid[r][c] == self.pick:
            self.grid[r][c] = 0
            self.message = "CLEARED"
            return

        self.grid[r][c] = self.pick
        if self.pick == SOLUTION[r][c]:
            self.message = "CORRECT"
        else:
            self.mistakes += 1
            self.message = "CHECK"

        if self.is_complete():
            self.message = "SOLVED"

    def is_complete(self) -> bool:
        for r in range(9):
            for c in range(9):
                if self.grid[r][c] != SOLUTION[r][c]:
                    return False
        return True

    def handle_game_action(self, action: str) -> str | None:
        if action == "back":
            return "exit"
        if action == "left":
            self.move_cursor()
            return "handled"
        if action == "right":
            self.cycle_number()
            return "handled"
        if action == "select":
            self.set_number()
            return "handled"
        return None

    def draw(self, surf: pygame.Surface, ui, state) -> None:
        state.active_app = "sudoku"
        ui.header(surf, "EXIT", "SET", state.led_color)

        ui.centered_text(surf, "SUDOKU", 42, COLORS.text, ui.font_md)

        grid_x = 12
        grid_y = 78
        cell = 24
        grid_size = cell * 9

        # outer board
        pygame.draw.rect(surf, COLORS.panel, (grid_x - 2, grid_y - 2, grid_size + 4, grid_size + 4), border_radius=3)

        # cells
        for r in range(9):
            for c in range(9):
                x = grid_x + c * cell
                y = grid_y + r * cell
                value = self.grid[r][c]
                is_fixed = PUZZLE[r][c] != 0
                is_cursor = (r, c) == self.cursor

                bg = (28, 34, 38)
                if is_cursor:
                    bg = (52, 72, 82)
                elif not is_fixed:
                    bg = (15, 18, 21)

                pygame.draw.rect(surf, bg, (x, y, cell - 1, cell - 1))

                if value:
                    if is_fixed:
                        color = COLORS.text
                    elif value == SOLUTION[r][c]:
                        color = COLORS.ok
                    else:
                        color = COLORS.warn

                    font = ui.font if is_fixed else ui.font_md
                    rendered = font.render(str(value), True, color)
                    surf.blit(
                        rendered,
                        (x + (cell - rendered.get_width()) // 2, y + (cell - rendered.get_height()) // 2 - 1),
                    )

        # grid lines, with heavy 3x3 boundaries
        for i in range(10):
            line_w = 3 if i % 3 == 0 else 1
            color = COLORS.text if i % 3 == 0 else COLORS.muted
            x = grid_x + i * cell
            y = grid_y + i * cell
            pygame.draw.line(surf, color, (x, grid_y), (x, grid_y + grid_size), line_w)
            pygame.draw.line(surf, color, (grid_x, y), (grid_x + grid_size, y), line_w)

        r, c = self.cursor
        selected_value = self.grid[r][c] or "-"
        ui.text(surf, f"PICK {self.pick}", 14, 302 - 40, COLORS.accent, ui.font_sm)
        ui.text(surf, f"CELL {r + 1},{c + 1}", 104, 302 - 40, COLORS.muted, ui.font_xs)
        ui.text(surf, self.message[:12], 14, 284, COLORS.text, ui.font_xs)
        ui.text(surf, f"MISS {self.mistakes}", 150, 284, COLORS.warn, ui.font_xs)

        ui.footer(surf, "CELL", "NUM")
