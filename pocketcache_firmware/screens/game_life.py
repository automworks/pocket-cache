from __future__ import annotations
import random, pygame
from .base import Screen
from ..theme import COLORS
class LifeScreen(Screen):
    name="game_life"
    def __init__(self): self.w=16; self.h=16; self.running=False; self.new()
    def new(self): self.grid=[[random.random()<.25 for _ in range(self.w)] for _ in range(self.h)]; self.gen=0
    def step(self):
        ng=[[False]*self.w for _ in range(self.h)]
        for r in range(self.h):
            for c in range(self.w):
                n=sum(self.grid[(r+dr)%self.h][(c+dc)%self.w] for dr in(-1,0,1) for dc in(-1,0,1) if dr or dc)
                ng[r][c]= n==3 or (self.grid[r][c] and n==2)
        self.grid=ng; self.gen+=1
    def handle_game_action(self,action):
        if action=="back": return "exit"
        if action=="left": self.step(); return "handled"
        if action=="right": self.new(); return "handled"
        if action=="select": self.running=not self.running; return "handled"
        return None
    def draw(self,surf,ui,state):
        state.active_app="life"; ui.header(surf,"life",state.led_color)
        if self.running and state.uptime_seconds % 1 == 0: self.step()
        ui.text(surf,"LIFE",16,44,COLORS.text,ui.font_lg); ui.text(surf,f"GEN {self.gen}",130,56,COLORS.muted,ui.font_xs)
        x0,y0,s=24,92,12
        for r in range(self.h):
            for c in range(self.w):
                if self.grid[r][c]: pygame.draw.rect(surf,COLORS.ok,(x0+c*s,y0+r*s,s-2,s-2))
                else: pygame.draw.rect(surf,COLORS.panel,(x0+c*s,y0+r*s,s-2,s-2))
        ui.footer(surf,"X EXIT  Y RUN  A STEP  B NEW")
