from __future__ import annotations

import pygame

from .theme import COLORS, WIDTH, HEADER_H, FOOTER_Y, FOOTER_H, PADDING


class UI:
    def __init__(self) -> None:
        pygame.font.init()

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

    def header(
        self,
        surf: pygame.Surface,
        back: str | None = "EXIT",
        select: str | None = None,
        led: tuple[int, int, int] | None = None,
    ) -> None:
        """Split header: X button label on left, Y button label on right, LED dot center."""
        pygame.draw.rect(surf, COLORS.panel, (0, 0, WIDTH, HEADER_H))
        if back:
            self.text(surf, f"x {back.upper()}", PADDING, 10, COLORS.muted, self.font_xs)
        if select:
            label = f"{select.upper()} o"
            rendered = self.font_xs.render(label, True, COLORS.muted)
            surf.blit(rendered, (WIDTH - PADDING - rendered.get_width(), 10))
        if led:
            pygame.draw.circle(surf, led, (WIDTH // 2, HEADER_H // 2), 5)
            pygame.draw.circle(surf, COLORS.bg, (WIDTH // 2, HEADER_H // 2), 6, 1)

    def footer(
        self,
        surf: pygame.Surface,
        prev: str | None = None,
        next: str | None = None,
    ) -> None:
        """Split footer: A button label on left, B button label on right."""
        pygame.draw.rect(surf, COLORS.panel, (0, FOOTER_Y, WIDTH, FOOTER_H))
        if prev:
            self.text(surf, f"< {prev.upper()}", PADDING, FOOTER_Y + 10, COLORS.muted, self.font_xs)
        if next:
            label = f"{next.upper()} >"
            rendered = self.font_xs.render(label, True, COLORS.muted)
            surf.blit(rendered, (WIDTH - PADDING - rendered.get_width(), FOOTER_Y + 10))

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
