from __future__ import annotations

import pygame

from ..theme import WIDTH, HEIGHT, COLORS


class PygameAdapter:
    def __init__(self, scale: int = 3) -> None:
        pygame.init()
        self.scale = scale
        self.logical = pygame.Surface((WIDTH, HEIGHT))
        self.window = pygame.display.set_mode((WIDTH * scale, HEIGHT * scale))
        pygame.display.set_caption("pocket-cache firmware v0 portrait")
        self.clock = pygame.time.Clock()
        self.running = True

    def clear(self) -> None:
        self.logical.fill(COLORS.bg)

    def present(self) -> None:
        scaled = pygame.transform.scale(self.logical, self.window.get_size())
        self.window.blit(scaled, (0, 0))
        pygame.display.flip()

    def poll(self) -> list[str]:
        actions: list[str] = []
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                actions.append("quit")
            elif event.type == pygame.KEYDOWN:
                key = event.key
                if key == pygame.K_q:
                    actions.append("quit")
                elif key in (pygame.K_x, pygame.K_ESCAPE, pygame.K_BACKSPACE):
                    actions.append("back")
                elif key in (pygame.K_y, pygame.K_RETURN, pygame.K_SPACE):
                    actions.append("select")
                elif key in (pygame.K_LEFT, pygame.K_a):
                    actions.append("left")
                elif key in (pygame.K_RIGHT, pygame.K_b):
                    actions.append("right")
                elif key == pygame.K_MINUS:
                    actions.append("battery")
                elif key == pygame.K_c:
                    actions.append("clients")
                elif key == pygame.K_e:
                    actions.append("error")
                elif key == pygame.K_r:
                    actions.append("reboot")
        return actions

    def fps(self, value: int = 30) -> None:
        self.clock.tick(value)

    def close(self) -> None:
        pygame.quit()
