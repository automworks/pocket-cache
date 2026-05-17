from __future__ import annotations

from .screens.boot import BootScreen
from .screens.menu import AppMenuScreen
from .screens.wifi import WifiScreen
from .screens.portal import PortalScreen
from .screens.status import StatusScreen
from .screens.library import LibraryScreen
from .screens.sudoku import SudokuScreen
from .screens.games_menu import GamesMenuScreen
from .screens.game_2048 import Game2048Screen
from .screens.game_mines import MinesScreen
from .screens.game_blackjack import BlackjackScreen
from .screens.game_chess import ChessScreen
from .screens.game_tetris import TetrisScreen
from .screens.game_life import LifeScreen
from .screens.game_dice import DiceScreen
from .screens.reader import ReaderScreen
from .screens.about import AboutScreen
from .screens.alert import AlertScreen
from .screens.settings import SettingsScreen


class ScreenRouter:
    def __init__(self, auto_cycle_seconds: float = 9.0) -> None:
        self.boot_screen = BootScreen()
        self.alert_screen = AlertScreen()
        self.menu_screen = AppMenuScreen()
        self.screens = {
            "menu": self.menu_screen,
            "about": AboutScreen(),
            "library": LibraryScreen(),
            "games": GamesMenuScreen(),
            "sudoku": SudokuScreen(),
            "game_2048": Game2048Screen(),
            "game_mines": MinesScreen(),
            "blackjack": BlackjackScreen(),
            "chess": ChessScreen(),
            "tetris": TetrisScreen(),
            "life": LifeScreen(),
            "dice": DiceScreen(),
            "reader": ReaderScreen(),
            "portal": PortalScreen(),
            "wifi": WifiScreen(),
            "status": StatusScreen(),
            "settings": SettingsScreen(),
        }
        self.active = "menu"
        self.last_input_at = 0
        self.auto_cycle_seconds = auto_cycle_seconds
        self.paused = True
        self.force_alert = False

    def current(self, state):
        if state.booting:
            state.active_app = "boot"
            return self.boot_screen
        if self.force_alert or (state.has_alert and not state.alert_acknowledged):
            state.active_app = "alert"
            return self.alert_screen
        return self.screens[self.active]

    def open(self, app_id: str) -> None:
        if app_id in self.screens:
            self.active = app_id

    def back_to_menu(self) -> None:
        self.active = "menu"
        self.force_alert = False

    def next(self) -> None:
        if self.active == "menu":
            self.menu_screen.handle_menu_action("right")
        else:
            self.back_to_menu()

    def previous(self) -> None:
        if self.active == "menu":
            self.menu_screen.handle_menu_action("left")
        else:
            self.back_to_menu()

    def tick(self, state) -> None:
        return

    def toggle_alert(self) -> None:
        self.force_alert = not self.force_alert
