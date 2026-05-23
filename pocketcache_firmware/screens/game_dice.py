from __future__ import annotations
import random, pygame
from .base import Screen
from ..theme import COLORS
class DiceScreen(Screen):
    name="game_dice"
    def __init__(self): self.sides=[4,6,8,10,12,20,100]; self.i=5; self.roll=random.randint(1,20)
    def handle_game_action(self,action):
        if action=="back": return "exit"
        if action=="left": self.i=(self.i-1)%len(self.sides); return "handled"
        if action=="right": self.i=(self.i+1)%len(self.sides); return "handled"
        if action=="select": self.roll=random.randint(1,self.sides[self.i]); return "handled"
        return None
    def draw(self,surf,ui,state):
        state.active_app="dice"; ui.header(surf, "EXIT", "ROLL", state.led_color)
        ui.centered_text(surf,f"D{self.sides[self.i]}",58,COLORS.muted,ui.font_md)
        ui.centered_text(surf,str(self.roll),112,COLORS.text,pygame.font.SysFont("dejavusansmono,consolas,monospace",72,bold=True))
        ui.centered_text(surf,"Y ROLL",220,state.app_accent_color,ui.font_md)
        ui.footer(surf, "DIE", "DIE")
