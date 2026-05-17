from __future__ import annotations
import random, pygame
from .base import Screen
from ..theme import COLORS
class ChessScreen(Screen):
    name="game_chess"
    def __init__(self): self.new()
    def new(self):
        self.board=[list("r...k..r"),list("pppppppp"),list("........"),list("........"),list("........"),list("........"),list("PPPPPPPP"),list("R...K..R")]
        self.cur=[6,0]; self.sel=None; self.msg="MICRO CHESS"
    def handle_game_action(self,action):
        if action=="back": return "exit"
        r,c=self.cur
        if action=="left": self.cur=[r,(c-1)%8]; return "handled"
        if action=="right": self.cur=[r,(c+1)%8]; return "handled"
        if action=="select":
            if self.sel is None and self.board[r][c].isupper(): self.sel=[r,c]; self.msg="SELECTED"
            elif self.sel:
                sr,sc=self.sel; p=self.board[sr][sc]
                if self.legal(sr,sc,r,c,p):
                    self.board[r][c]=p; self.board[sr][sc]="."; self.sel=None; self.bot(); self.msg="BOT MOVED"
                else: self.sel=None; self.msg="CANCEL"
            return "handled"
        return None
    def legal(self,sr,sc,r,c,p):
        if (sr,sc)==(r,c): return False
        if self.board[r][c].isupper(): return False
        dr,dc=r-sr,c-sc
        if p=="P": return (dr==-1 and dc==0 and self.board[r][c]==".") or (dr==-1 and abs(dc)==1 and self.board[r][c].islower())
        if p=="K": return abs(dr)<=1 and abs(dc)<=1
        if p=="R": return sr==r or sc==c
        return False
    def bot(self):
        moves=[]
        for sr in range(8):
            for sc in range(8):
                p=self.board[sr][sc]
                if not p.islower(): continue
                for r in range(8):
                    for c in range(8):
                        if self.legal_black(sr,sc,r,c,p): moves.append((sr,sc,r,c,p))
        if moves:
            sr,sc,r,c,p=random.choice(moves); self.board[r][c]=p; self.board[sr][sc]="."
    def legal_black(self,sr,sc,r,c,p):
        if self.board[r][c].islower(): return False
        dr,dc=r-sr,c-sc
        if p=="p": return (dr==1 and dc==0 and self.board[r][c]==".") or (dr==1 and abs(dc)==1 and self.board[r][c].isupper())
        if p=="k": return abs(dr)<=1 and abs(dc)<=1
        if p=="r": return sr==r or sc==c
        return False
    def draw(self,surf,ui,state):
        state.active_app="chess"; ui.header(surf, "EXIT", "SEL", state.led_color)
        ui.text(surf,"CHESS BOT",16,42,COLORS.text,ui.font_md); ui.text(surf,self.msg[:12],16,66,COLORS.muted,ui.font_xs)
        x0,y0,s=24,92,24
        for r in range(8):
            for c in range(8):
                bg=(40,45,48) if (r+c)%2 else (24,29,32)
                if [r,c]==self.cur: bg=(52,72,82)
                if self.sel==[r,c]: bg=(80,60,30)
                pygame.draw.rect(surf,bg,(x0+c*s,y0+r*s,s-1,s-1))
                p=self.board[r][c]
                if p!=".": surf.blit(ui.font.render(p,True,COLORS.text if p.isupper() else COLORS.bad),(x0+c*s+6,y0+r*s+3))
        ui.footer(surf, "MOVE", "MOVE")
