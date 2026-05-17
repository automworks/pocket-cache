from __future__ import annotations
import random
import pygame
from .base import Screen
from ..theme import COLORS

class MinesScreen(Screen):
    name = "game_mines"
    def __init__(self):
        self.w, self.h, self.mines = 6, 6, 6
        self.new_game()
    def new_game(self):
        self.cursor = [0,0]; self.revealed=set(); self.flags=set(); self.dead=False; self.win=False
        cells=[(r,c) for r in range(self.h) for c in range(self.w)]
        self.mine_cells=set(random.sample(cells,self.mines))
        self.msg="MINES"
    def count(self,r,c):
        return sum((rr,cc) in self.mine_cells for rr in range(r-1,r+2) for cc in range(c-1,c+2) if (rr,cc)!=(r,c))
    def reveal(self,r,c):
        if (r,c) in self.flags: return
        if (r,c) in self.mine_cells:
            self.dead=True; self.msg="BOOM"; self.revealed.add((r,c)); return
        stack=[(r,c)]
        while stack:
            cell=stack.pop()
            if cell in self.revealed or cell in self.flags: continue
            self.revealed.add(cell)
            rr,cc=cell
            if self.count(rr,cc)==0:
                for nr in range(max(0,rr-1),min(self.h,rr+2)):
                    for nc in range(max(0,cc-1),min(self.w,cc+2)):
                        if (nr,nc) not in self.revealed: stack.append((nr,nc))
        if len(self.revealed) == self.w*self.h-self.mines:
            self.win=True; self.msg="CLEAR"
    def handle_game_action(self, action):
        if action=="back": return "exit"
        if self.dead or self.win:
            if action=="select": self.new_game(); return "handled"
        r,c=self.cursor
        if action=="left": self.cursor=[r,(c-1)%self.w]; return "handled"
        if action=="right": self.cursor=[r,(c+1)%self.w]; return "handled"
        if action=="select": self.reveal(r,c); return "handled"
        return None
    def draw(self,surf,ui,state):
        state.active_app="game_mines"; ui.header(surf,"mines",state.led_color)
        ui.text(surf,"MINES",16,44,COLORS.text,ui.font_lg); ui.text(surf,self.msg,130,56,COLORS.accent,ui.font_xs)
        x0,y0,cell=24,104,32
        for r in range(self.h):
            for c in range(self.w):
                x=x0+c*cell; y=y0+r*cell; cur=[r,c]==self.cursor
                bg=(52,72,82) if cur else COLORS.panel
                pygame.draw.rect(surf,bg,(x,y,cell-3,cell-3),border_radius=5)
                if (r,c) in self.revealed:
                    if (r,c) in self.mine_cells:
                        ui.centered_text(surf,"*",y+6,COLORS.bad,ui.font_md)
                        surf.blit(ui.font_md.render("*",True,COLORS.bad),(x+9,y+3))
                    else:
                        n=self.count(r,c)
                        if n: surf.blit(ui.font.render(str(n),True,COLORS.text),(x+10,y+6))
                        else: pygame.draw.rect(surf,(20,25,28),(x,y,cell-3,cell-3),border_radius=5)
        ui.footer(surf,"X EXIT  Y OPEN  A/B MOVE")
