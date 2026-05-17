from __future__ import annotations
import random
import pygame
from .base import Screen
from ..theme import COLORS

class BlackjackScreen(Screen):
    name="game_blackjack"
    def __init__(self): self.new_round()
    def card(self): return random.choice([2,3,4,5,6,7,8,9,10,10,10,10,11])
    def total(self,hand):
        t=sum(hand); aces=sum(1 for c in hand if c==11)
        while t>21 and aces: t-=10; aces-=1
        return t
    def new_round(self):
        self.player=[self.card(),self.card()]; self.dealer=[self.card(),self.card()]
        self.done=False; self.msg="HIT OR STAND"
    def hit(self):
        if self.done: self.new_round(); return
        self.player.append(self.card())
        if self.total(self.player)>21: self.done=True; self.msg="BUST"
    def stand(self):
        if self.done: self.new_round(); return
        while self.total(self.dealer)<17: self.dealer.append(self.card())
        pt,dt=self.total(self.player),self.total(self.dealer)
        self.done=True
        self.msg="WIN" if dt>21 or pt>dt else "PUSH" if pt==dt else "LOSE"
    def handle_game_action(self, action):
        if action=="back": return "exit"
        if action=="left": self.hit(); return "handled"
        if action=="right" or action=="select": self.stand(); return "handled"
        return None
    def draw_hand(self,surf,ui,label,hand,y,hide=False):
        ui.text(surf,label,16,y,COLORS.muted,ui.font_xs)
        x=16
        shown=hand if not hide else [hand[0],0]
        for c in shown:
            pygame.draw.rect(surf,COLORS.panel,(x,y+24,38,48),border_radius=6)
            txt="?" if c==0 else ("A" if c==11 else str(c))
            surf.blit(ui.font.render(txt,True,COLORS.text),(x+10,y+38)); x+=44
    def draw(self,surf,ui,state):
        state.active_app="blackjack"; ui.header(surf,"blackjack",state.led_color)
        ui.text(surf,"BLACKJACK",16,44,COLORS.text,ui.font_md)
        self.draw_hand(surf,ui,"DEALER",self.dealer,82,hide=not self.done)
        self.draw_hand(surf,ui,"YOU",self.player,180)
        ui.text(surf,self.msg,16,276,COLORS.accent,ui.font_xs)
        ui.footer(surf,"X EXIT  A HIT  B/Y STAND")
