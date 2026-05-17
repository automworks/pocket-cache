from __future__ import annotations

import textwrap
import pygame

from .base import Screen
from ..theme import COLORS, WIDTH


SAMPLE_TEXT = """
POCKET-CACHE FIELD NOTES

Pocket-cache is a small offline knowledge hub for camping, outages, travel, and anywhere the network is unavailable.

This simple reader is intentionally basic. It is designed for short field references, notes, checklists, public-domain excerpts, survival cards, repair instructions, and plain text documents.

The first goal is not a full ebook system. The goal is to prove that reading on the tiny LCD is possible with predictable controls.

Suggested content for future builds:

- First-aid quick reference
- Camp setup checklist
- Power and battery notes
- Local map notes
- Device troubleshooting
- Short public-domain books
- Interactive fiction hints

The reader uses large bold monospace text because thin small fonts are hard to read on the two-inch display.

Controls are now consistent across firmware:

A is Back.
B is Select.
X is Left.
Y is Right.

Inside the reader, left and right move between pages. Back exits to the firmware carousel. Select toggles the text size.

End of sample.
""".strip()


class ReaderScreen(Screen):
    name = "reader"

    def __init__(self) -> None:
        self.title = "Field Notes"
        self.text = SAMPLE_TEXT
        self.page = 0
        self.large_text = False
        self._cached_pages_key = None
        self._pages: list[list[str]] = []

    def _wrap_pages(self, ui) -> list[list[str]]:
        font = ui.font if not self.large_text else ui.font_md
        # conservative char width for bold mono on 240px portrait
        max_chars = 22 if not self.large_text else 17
        lines_per_page = 11 if not self.large_text else 8

        key = (self.large_text, max_chars, lines_per_page)
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
            return "exit"
        if action == "left":
            self.page = max(0, self.page - 1)
            return "handled"
        if action == "right":
            # page max is clamped during draw after pages are calculated
            self.page += 1
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
        ui.centered_text(surf, f"PAGE {self.page + 1}/{len(pages)}", 64, COLORS.muted, ui.font_xs)

        y = 92
        font = ui.font if not self.large_text else ui.font_md
        line_h = 19 if not self.large_text else 25

        for line in page_lines:
            if line == "":
                y += line_h
                continue
            ui.text(surf, line, 12, y, COLORS.text, font)
            y += line_h

        # progress bar
        pct = int(((self.page + 1) / len(pages)) * 100)
        ui.progress_bar(surf, 12, 278, WIDTH - 24, 10, pct, COLORS.accent)

        ui.footer(surf, "PREV", "NEXT")
