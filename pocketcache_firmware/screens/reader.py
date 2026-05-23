from __future__ import annotations

import textwrap
from pathlib import Path
import pygame

from .base import Screen
from ..theme import COLORS, WIDTH

_DATA_DIR = Path(__file__).parent.parent / "data"

_DOCS: list[tuple[str, str]] = [
    ("Field Guide", "field_guide.txt"),
    ("First Aid", "first_aid.txt"),
]


def _load(filename: str) -> str:
    path = _DATA_DIR / filename
    try:
        return path.read_text(encoding="utf-8").strip()
    except OSError:
        return f"File not found:\n{filename}"


class ReaderScreen(Screen):
    name = "reader"

    def __init__(self) -> None:
        self.doc_index = 0
        self._load_doc()
        self.page = 0
        self.large_text = False
        self._cached_pages_key = None
        self._pages: list[list[str]] = []

    def _load_doc(self) -> None:
        title, filename = _DOCS[self.doc_index]
        self.title = title
        self.text = _load(filename)
        self._cached_pages_key = None
        self._pages = []
        self.page = 0

    def _wrap_pages(self, ui) -> list[list[str]]:
        max_chars = 22 if not self.large_text else 17
        lines_per_page = 11 if not self.large_text else 8

        key = (self.doc_index, self.large_text, max_chars, lines_per_page)
        if self._cached_pages_key == key and self._pages:
            return self._pages

        lines: list[str] = []
        for para in self.text.split("\n"):
            para = para.strip()
            if not para:
                lines.append("")
                continue
            wrapped = textwrap.wrap(para, width=max_chars)
            lines.extend(wrapped)

        pages: list[list[str]] = []
        current: list[str] = []
        for line in lines:
            current.append(line)
            if len(current) >= lines_per_page:
                pages.append(current)
                current = []
        if current:
            pages.append(current)

        self._pages = pages or [["No text loaded."]]
        self._cached_pages_key = key
        self.page = max(0, min(self.page, len(self._pages) - 1))
        return self._pages

    def handle_reader_action(self, action: str) -> str | None:
        if action == "back":
            if self.page > 0:
                self.page = 0
                return "handled"
            # cycle to previous document
            self.doc_index = (self.doc_index - 1) % len(_DOCS)
            self._load_doc()
            return "handled" if self.doc_index != 0 else "exit"
        if action == "left":
            if self.page > 0:
                self.page -= 1
            else:
                self.doc_index = (self.doc_index - 1) % len(_DOCS)
                self._load_doc()
            return "handled"
        if action == "right":
            pages = self._pages or self._wrap_pages(None)  # type: ignore[arg-type]
            if self.page < len(pages) - 1:
                self.page += 1
            else:
                self.doc_index = (self.doc_index + 1) % len(_DOCS)
                self._load_doc()
            return "handled"
        if action == "select":
            self.large_text = not self.large_text
            self._cached_pages_key = None
            return "handled"
        return None

    def draw(self, surf: pygame.Surface, ui, state) -> None:
        state.active_app = "reader"
        ui.header(surf, "EXIT", "SIZE", state.led_color)

        pages = self._wrap_pages(ui)
        self.page = max(0, min(self.page, len(pages) - 1))
        page_lines = pages[self.page]

        ui.centered_text(surf, self.title.upper(), 42, COLORS.text, ui.font_sm)
        ui.centered_text(surf, f"PAGE {self.page + 1}/{len(pages)}", 62, COLORS.muted, ui.font_xs)

        # doc dots
        accent = state.app_accent_color
        dot_size, gap = 6, 8
        total_w = len(_DOCS) * (dot_size + gap) - gap
        dot_x = (WIDTH - total_w) // 2
        for i in range(len(_DOCS)):
            color = accent if i == self.doc_index else COLORS.muted
            pygame.draw.rect(surf, color, (dot_x + i * (dot_size + gap), 76, dot_size, dot_size), border_radius=2)

        y = 92
        font = ui.font if not self.large_text else ui.font_md
        line_h = 19 if not self.large_text else 25

        for line in page_lines:
            if line == "":
                y += line_h // 2
                continue
            ui.text(surf, line, 12, y, COLORS.text, font)
            y += line_h

        pct = int(((self.page + 1) / len(pages)) * 100)
        ui.progress_bar(surf, 12, 262, WIDTH - 24, 10, pct, accent)

        ui.footer(surf, "PREV", "NEXT")
