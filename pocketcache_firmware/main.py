from __future__ import annotations

from time import monotonic

from .adapters.pygame_adapter import PygameAdapter
from .router import ScreenRouter
from .state import DeviceState
from .ui import UI
from .config_manager import load_config, apply_runtime_config_to_state


def handle_actions(actions: list[str], state: DeviceState, router: ScreenRouter, adapter: PygameAdapter) -> None:
    for action in actions:
        current_screen = router.current(state)
        name = getattr(current_screen, "name", "")

        if name == "menu":
            result = current_screen.handle_menu_action(action)
            if result == "handled":
                router.last_input_at = monotonic()
                continue
            if result:
                router.open(result)
                router.last_input_at = monotonic()
                continue


        if name == "games_menu":
            result = current_screen.handle_games_menu_action(action)
            if result == "handled":
                router.last_input_at = monotonic()
                continue
            if result == "exit":
                router.back_to_menu()
                router.last_input_at = monotonic()
                continue
            if result:
                router.open(result)
                router.last_input_at = monotonic()
                continue

        if name in ("game_2048", "game_mines", "blackjack", "chess", "tetris", "life", "dice"):
            result = current_screen.handle_game_action(action)
            if result == "handled":
                router.last_input_at = monotonic()
                continue
            if result == "exit":
                router.open("games")
                router.last_input_at = monotonic()
                continue

        if name == "sudoku":
            result = current_screen.handle_game_action(action)
            if result == "handled":
                router.last_input_at = monotonic()
                continue
            if result == "exit":
                router.open("games")
                router.last_input_at = monotonic()
                continue

        if name == "reader":
            result = current_screen.handle_reader_action(action)
            if result == "handled":
                router.last_input_at = monotonic()
                continue
            if result == "exit":
                router.back_to_menu()
                router.last_input_at = monotonic()
                continue

        if name == "portal":
            result = current_screen.handle_portal_action(action)
            if result == "handled":
                router.last_input_at = monotonic()
                continue
            if result == "exit":
                router.back_to_menu()
                router.last_input_at = monotonic()
                continue

        if name == "settings":
            result = current_screen.handle_settings_action(action, state)
            if result == "handled":
                router.last_input_at = monotonic()
                continue
            if result == "exit":
                router.back_to_menu()
                router.last_input_at = monotonic()
                continue

        if action == "quit":
            adapter.running = False
        elif action == "back":
            router.back_to_menu()
            if state.has_alert:
                state.alert_acknowledged = True
                router.force_alert = False
        elif action == "right":
            if router.active == "menu":
                router.menu_screen.handle_menu_action("right")
            else:
                router.back_to_menu()
        elif action == "left":
            if router.active == "menu":
                router.menu_screen.handle_menu_action("left")
            else:
                router.back_to_menu()
        elif action == "select":
            state.toggle_selected()
            if state.has_alert:
                state.alert_acknowledged = True
                router.force_alert = False
        elif action == "battery":
            state.drain_battery()
            state.alert_acknowledged = False
        elif action == "clients":
            state.cycle_clients()
        elif action == "error":
            state.toggle_kiwix_error()
            state.alert_acknowledged = False
        elif action == "reboot":
            state.reboot()
            router.back_to_menu()


def main() -> None:
    adapter = PygameAdapter(scale=3)
    ui = UI()
    state = DeviceState()
    apply_runtime_config_to_state(state, load_config())
    router = ScreenRouter(auto_cycle_seconds=9.0)

    try:
        while adapter.running:
            actions = adapter.poll()
            handle_actions(actions, state, router, adapter)

            state.tick()
            router.tick(state)

            adapter.clear()
            screen = router.current(state)
            screen.draw(adapter.logical, ui, state)
            adapter.present()
            adapter.fps(30)
    finally:
        adapter.close()


if __name__ == "__main__":
    main()
