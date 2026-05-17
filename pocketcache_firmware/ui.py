from __future__ import annotations

import pygame

from .theme import COLORS, WIDTH, HEADER_H, FOOTER_Y, FOOTER_H, PADDING


class UI:
    def __init__(self) -> None:
        pygame.font.init()

        # On the real 2" LCD, thin small fonts are hard to read. Keep everything
        # bold/mono and avoid sizes below 14px.
        mono = "dejavusansmono,consolas,menlo,monospace"
        self.font_xs = pygame.font.SysFont(mono, 14, bold=True)
        self.font_sm = pygame.font.SysFont(mono, 15, bold=True)
        self.font = pygame.font.SysFont(mono, 17, bold=True)
        self.font_md = pygame.font.SysFont(mono, 21, bold=True)
        self.font_lg = pygame.font.SysFont(mono, 30, bold=True)

    def text(self, surf: pygame.Surface, text: str, x: int, y: int, color=COLORS.text, font=None) -> None:
        font = font or self.font
        surf.blit(font.render(text, True, color), (x, y))

    def centered_text(self, surf: pygame.Surface, text: str, y: int, color=COLORS.text, font=None) -> None:
        font = font or self.font
        rendered = font.render(text, True, color)
        surf.blit(rendered, ((WIDTH - rendered.get_width()) // 2, y))

    def header(self, surf: pygame.Surface, title: str, led: tuple[int, int, int]) -> None:
        pygame.draw.rect(surf, COLORS.panel, (0, 0, WIDTH, HEADER_H))
        self.text(surf, title.upper(), PADDING, 8, COLORS.text, self.font_xs)
        pygame.draw.circle(surf, led, (WIDTH - 17, HEADER_H // 2), 7)
        pygame.draw.circle(surf, COLORS.bg, (WIDTH - 17, HEADER_H // 2), 8, 1)

    def footer(self, surf: pygame.Surface, label: str = "A BACK  B NEXT  X OK") -> None:
        pygame.draw.rect(surf, COLORS.panel, (0, FOOTER_Y, WIDTH, FOOTER_H))
        self.centered_text(surf, label.upper(), FOOTER_Y + 9, COLORS.muted, self.font_xs)

    def progress_bar(
        self,
        surf: pygame.Surface,
        x: int,
        y: int,
        w: int,
        h: int,
        pct: int,
        color: tuple[int, int, int],
    ) -> None:
        pct = max(0, min(100, pct))
        pygame.draw.rect(surf, COLORS.panel, (x, y, w, h), border_radius=4)
        pygame.draw.rect(surf, color, (x, y, int(w * pct / 100), h), border_radius=4)
        pygame.draw.rect(surf, COLORS.muted, (x, y, w, h), 1, border_radius=4)

    def status_chip(self, surf: pygame.Surface, label: str, ok: bool, x: int, y: int, w: int = 104) -> None:
        color = COLORS.ok if ok else COLORS.bad
        pygame.draw.rect(surf, COLORS.panel, (x, y, w, 27), border_radius=6)
        pygame.draw.circle(surf, color, (x + 13, y + 13), 6)
        self.text(surf, label[:10].upper(), x + 27, y + 5, COLORS.text, self.font_xs)

    def divider(self, surf: pygame.Surface, y: int) -> None:
        pygame.draw.line(surf, COLORS.panel, (PADDING, y), (WIDTH - PADDING, y), 2)
