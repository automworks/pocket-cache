from __future__ import annotations
import random, pygame
from .base import Screen
from ..theme import COLORS
PIECES=[[(0,0),(1,0),(0,1),(1,1)],[(0,0),(-1,0),(1,0),(2,0)],[(0,0),(0,1),(1,1),(-1,1)],[(0,0),(0,1),(0,2),(1,2)]]
class TetrisScreen(Screen):
    name="game_tetris"
    def __init__(self): self.w=10; self.h=18; self.new()
    def new(self): self.grid=[[0]*self.w for _ in range(self.h)]; self.score=0; self.spawn(); self.msg="TETRIS"
    def spawn(self): self.piece=random.choice(PIECES); self.x=5; self.y=0
    def cells(self): return [(self.x+dx,self.y+dy) for dx,dy in self.piece]
    def hit(self,dx=0,dy=0):
        for x,y in [(x+dx,y+dy) for x,y in self.cells()]:
            if x<0 or x>=self.w or y>=self.h: return True
            if y>=0 and self.grid[y][x]: return True
        return False
    def lock(self):
        for x,y in self.cells():
            if 0<=y<self.h and 0<=x<self.w: self.grid[y][x]=1
        self.grid=[row for row in self.grid if not all(row)]
        cleared=self.h-len(self.grid); self.score+=cleared*100
        while len(self.grid)<self.h: self.grid.insert(0,[0]*self.w)
        self.spawn()
        if self.hit(): self.msg="GAME OVER"; self.new()
    def drop(self):
        if not self.hit(dy=1): self.y+=1
        else: self.lock()
    def rotate(self):
        old=self.piece; self.piece=[(-dy,dx) for dx,dy in self.piece]
        if self.hit(): self.piece=old
    def handle_game_action(self,action):
        if action=="back": return "exit"
        if action=="left" and not self.hit(dx=-1): self.x-=1; return "handled"
        if action=="right" and not self.hit(dx=1): self.x+=1; return "handled"
        if action=="select": self.rotate(); self.drop(); return "handled"
        return "handled" if action in ("left","right","select") else None
    def draw(self,surf,ui,state):
        state.active_app="tetris"; ui.header(surf,"tetris",state.led_color); self.drop()
        ui.text(surf,"TETRIS",16,42,COLORS.text,ui.font_md); ui.text(surf,f"{self.score}",140,47,COLORS.muted,ui.font_xs)
        x0,y0,s=45,78,15
        active=set(self.cells())
        for r in range(self.h):
            for c in range(self.w):
                on=self.grid[r][c] or (c,r) in active
                pygame.draw.rect(surf,COLORS.accent if on else COLORS.panel,(x0+c*s,y0+r*s,s-2,s-2))
        ui.footer(surf,"X EXIT  Y ROT  A/B MOVE")
